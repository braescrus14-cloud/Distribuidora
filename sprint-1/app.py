import argparse
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from getpass import getpass
import hashlib
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen
from urllib.error import URLError
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook


ROOT = Path(__file__).resolve().parent
DB = Path(os.environ.get("VILLALI_DATABASE", ROOT / "villali.sqlite3"))
ROLES = {
    "01": "Gerente General", "02": "Administrador del Sistema",
    "03": "Jefe de Bodega", "04": "Auxiliar de Bodega",
    "05": "Coordinador de Compras", "06": "Asesor Comercial",
    "07": "Coordinador de Logística y Despachos", "08": "Conductor",
    "09": "Auxiliar Contable y de Facturación", "10": "Cliente",
}
CATALOG = set(ROLES) - {"08"}
INVENTORY = {"01", "02", "03", "04", "05", "07", "09"}
HEADERS = ("sku", "lote", "vencimiento", "cantidad", "ubicacion")
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
    password TEXT, role TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
    failures INTEGER NOT NULL DEFAULT 0, locked_until INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
    last_seen INTEGER NOT NULL, timeout INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS invitations (
    token TEXT PRIMARY KEY, user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS user_contacts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, sku TEXT UNIQUE NOT NULL, barcode TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL, brand TEXT NOT NULL, species TEXT NOT NULL,
    presentation TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    minimum INTEGER NOT NULL CHECK(minimum > 0), active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS imports (
    id INTEGER PRIMARY KEY CHECK(id = 1), digest TEXT NOT NULL, row_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS catalog_sources (
    product_id INTEGER PRIMARY KEY REFERENCES products(id),
    source_key TEXT NOT NULL UNIQUE,
    price_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lots (
    product_id INTEGER NOT NULL REFERENCES products(id), lot TEXT NOT NULL,
    expiry TEXT NOT NULL, location TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity >= 0),
    reserved INTEGER NOT NULL DEFAULT 0 CHECK(reserved BETWEEN 0 AND quantity),
    PRIMARY KEY(product_id, lot, location)
);
CREATE INDEX IF NOT EXISTS lots_expiry ON lots(product_id, expiry);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY, at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor TEXT NOT NULL, event TEXT NOT NULL, ip TEXT NOT NULL, detail TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
BEGIN SELECT RAISE(ABORT, 'La auditoría es de solo anexado'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
BEGIN SELECT RAISE(ABORT, 'La auditoría es de solo anexado'); END;
"""


class Problem(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class PostgresDatabase:
    def __init__(self, url):
        import psycopg
        from psycopg.rows import dict_row

        self.integrity_error = psycopg.IntegrityError
        self.connection = psycopg.connect(
            url, autocommit=True, row_factory=dict_row, connect_timeout=15,
            cursor_factory=psycopg.ClientCursor,
        )

    def execute(self, sql, params=None):
        try:
            return self.connection.execute(sql.replace("?", "%s"), params)
        except self.integrity_error as error:
            raise sqlite3.IntegrityError(str(error)) from error

    def executemany(self, sql, rows):
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(sql.replace("?", "%s"), rows)
        except self.integrity_error as error:
            raise sqlite3.IntegrityError(str(error)) from error

    def close(self):
        self.connection.close()


@contextmanager
def database():
    mongo_uri = os.environ.get("MONGODB_URI")
    if mongo_uri:
        from mongo_store import MongoDatabase

        yield MongoDatabase(mongo_uri, os.environ.get("MONGODB_DATABASE", "villali"))
        return
    url = os.environ.get("DATABASE_URL")
    if url:
        db = PostgresDatabase(url)
    else:
        db = sqlite3.connect(DB, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction(db):
    if hasattr(db, "run"):
        with db.transaction():
            yield
        return
    if isinstance(db, PostgresDatabase):
        with db.connection.transaction():
            # Keep the single-writer behavior of SQLite BEGIN IMMEDIATE.
            db.execute("SELECT pg_advisory_xact_lock(63216801)")
            yield
        return
    db.execute("BEGIN IMMEDIATE")
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def initialize_schema(db):
    if hasattr(db, "run"):
        db.initialize()
        return
    if not isinstance(db, PostgresDatabase):
        db.executescript(SCHEMA)
        return
    schema = SCHEMA.split("CREATE TRIGGER", 1)[0]
    schema = schema.replace("id INTEGER PRIMARY KEY,", "id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,")
    schema = schema.replace("price_cents INTEGER", "price_cents BIGINT")
    schema = schema.replace("TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP",
                            "TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP::text)")
    with transaction(db):
        db.execute(schema)
        db.execute("""
            CREATE OR REPLACE FUNCTION villali_audit_append_only() RETURNS trigger
            LANGUAGE plpgsql AS $$ BEGIN
                RAISE EXCEPTION 'La auditoría es de solo anexado';
            END; $$;
            DROP TRIGGER IF EXISTS villali_audit_no_changes ON audit;
            CREATE TRIGGER villali_audit_no_changes BEFORE UPDATE OR DELETE ON audit
            FOR EACH ROW EXECUTE FUNCTION villali_audit_append_only();
        """)


def run_db(db, operation, sql, params=()):
    if hasattr(db, "run"):
        return db.run(operation, params)
    if operation == "lots_add":
        return db.executemany(sql, params)
    return db.execute(sql, params)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000)
    return f"{salt}:{key.hex()}"


def valid_password(value):
    if (not isinstance(value, str) or not 10 <= len(value) <= 128
            or not re.search(r"[A-Z]", value) or not re.search(r"[0-9]", value)
            or not re.search(r"[^\w\s]", value)):
        raise Problem("Usa 10 a 128 caracteres con mayúscula, número y símbolo.")
    return value


def field(data, key, limit=120):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise Problem(f"Revisa el campo {key}.")
    return value.strip()


def integer(value, minimum=0):
    if isinstance(value, bool) or not re.fullmatch(r"\d{1,9}", str(value)):
        raise ValueError
    result = int(value)
    if result < minimum:
        raise ValueError
    return result


def audit(db, actor, event, ip, detail=""):
    run_db(db, "audit_add", "INSERT INTO audit(actor,event,ip,detail) VALUES(?,?,?,?)",
               (actor, event, ip, detail))


def send_email(recipient, subject, message, event_key):
    key, sender = os.environ.get("RESEND_API_KEY"), os.environ.get("VILLALI_MAIL_FROM")
    if not recipient or not key or not sender:
        return "sin_configurar"
    payload = json.dumps({"from": sender, "to": [recipient], "subject": subject,
                          "text": message}).encode()
    request = Request("https://api.resend.com/emails", data=payload, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "Idempotency-Key": event_key, "User-Agent": "Villali/1.0",
    })
    try:
        with urlopen(request, timeout=5) as response:
            return "aceptado" if 200 <= response.status < 300 else "error"
    except (URLError, OSError):
        return "error"


def template():
    book = Workbook()
    sheet = book.active
    sheet.title = "Inventario"
    sheet.append(HEADERS)
    output = BytesIO()
    book.save(output)
    return output.getvalue()


def inventory_rows(db, raw):
    products = {row["sku"]: row["id"] for row in run_db(db, "active_products", 
        "SELECT id,sku FROM products WHERE active=1")}
    rows, errors, seen, lot_expiries = [], [], set(), {}
    try:
        with ZipFile(BytesIO(raw)) as archive:
            if sum(entry.file_size for entry in archive.infolist()) > 32_000_000:
                raise Problem("El Excel supera el tamaño máximo descomprimido.")
        book = load_workbook(BytesIO(raw), read_only=True, keep_links=False)
    except Problem:
        raise
    except Exception as error:
        raise Problem("Selecciona un archivo .xlsx válido.") from error
    try:
        sheet = book.active
        sheet.reset_dimensions()
        source = sheet.iter_rows(values_only=True, max_col=len(HEADERS))
        header = tuple(str(cell or "").strip().lower() for cell in next(source, ()))
        if header != HEADERS:
            raise Problem("Los encabezados deben coincidir con la plantilla.")
        for number, values in enumerate(source, 2):
            if number > 10001:
                raise Problem("El máximo es de 10 000 filas de datos.")
            if all(value is None for value in values):
                continue
            sku, lot, expiry, quantity, location = values
            sku = str(sku or "").strip().upper()
            lot = str(lot or "").strip()
            location = str(location or "").strip()
            try:
                if sku not in products:
                    raise ValueError("SKU inexistente o inactivo")
                if not lot or not location or len(lot) > 120 or len(location) > 120:
                    raise ValueError("Lote y ubicación son obligatorios")
                if lot.upper().startswith("DEMO-IT-"):
                    raise ValueError("El prefijo DEMO-IT- está reservado para lotes de demostración")
                if isinstance(expiry, datetime):
                    expiry = expiry.date()
                if not isinstance(expiry, date):
                    try:
                        expiry = date.fromisoformat(str(expiry))
                    except ValueError:
                        raise ValueError("Vencimiento inválido. Usa AAAA-MM-DD") from None
                if expiry <= date.today():
                    raise ValueError("El vencimiento debe ser futuro")
                try:
                    quantity = integer(quantity)
                except ValueError:
                    raise ValueError("Cantidad entera no negativa requerida") from None
                key = (sku, lot, location)
                lot_key = (sku, lot)
                if key in seen:
                    raise ValueError("SKU, lote y ubicación duplicados")
                if lot_key in lot_expiries and lot_expiries[lot_key] != expiry:
                    raise ValueError("El lote tiene fechas de vencimiento distintas")
                seen.add(key)
                lot_expiries[lot_key] = expiry
                rows.append((products[sku], lot, expiry.isoformat(), location, quantity))
            except ValueError as error:
                errors.append({"fila": number, "motivo": str(error)})
    except Problem:
        raise
    except Exception as error:
        raise Problem("No se pudo leer la hoja de inventario.") from error
    finally:
        book.close()
    if not rows and not errors:
        raise Problem("La hoja no contiene filas de inventario.")
    return rows, errors


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def respond(self, value, status=200, content_type="application/json; charset=utf-8", **headers):
        raw = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        for key, val in headers.items():
            self.send_header(key.replace("_", "-"), val)
        self.end_headers()
        self.wfile.write(raw)

    def body(self, maximum):
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise Problem("Longitud de solicitud inválida.") from None
        if not 0 < size <= maximum:
            raise Problem("Solicitud vacía o demasiado grande.", 413)
        return self.rfile.read(size)

    def data(self):
        if self.headers.get_content_type() != "application/json":
            raise Problem("Se requiere JSON.", 415)
        try:
            result = json.loads(self.body(32768))
        except (ValueError, UnicodeError):
            raise Problem("JSON inválido.") from None
        if not isinstance(result, dict):
            raise Problem("JSON inválido.")
        return result

    def handle_request(self, method):
        target = urlsplit(self.path)
        path = target.path
        try:
            if (method, path) == ("GET", "/health"):
                with database() as db:
                    run_db(db, "health", "SELECT 1 FROM users LIMIT 1").fetchone()
                return self.respond({"status": "ok"})
            if self.headers.get("Host") != urlsplit(self.server.origin).netloc:
                raise Problem("Abre la URL indicada por el servidor.", 403)
            if method == "GET" and path in {"/", "/app.js", "/style.css"}:
                files = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
                         "/style.css": ("style.css", "text/css")}
                name, kind = files[path]
                return self.respond((ROOT / name).read_bytes(), content_type=f"{kind}; charset=utf-8")
            if method == "POST" and self.headers.get("Origin") != self.server.origin:
                raise Problem("Origen no autorizado. Abre la URL indicada por el servidor.", 403)
            with database() as db:
                return self.api(db, method, path, parse_qs(target.query))
        except Problem as error:
            return self.respond({"error": str(error)}, error.status)
        except sqlite3.IntegrityError:
            return self.respond({"error": "El cambio entra en conflicto con un registro existente."}, 409)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            import traceback
            traceback.print_exc()
            return self.respond({"error": "Ocurrió un error interno."}, 500)

    @property
    def ip(self):
        return self.client_address[0]

    def session_key(self):
        cookies = SimpleCookie(self.headers.get("Cookie", ""))
        token = cookies.get("villali")
        return digest(token.value) if token else ""

    def session_cookie(self, token, expire=False):
        cookie = f"villali={token}; Path=/; HttpOnly; SameSite=Strict"
        if self.server.origin.startswith("https://"):
            cookie += "; Secure"
        return cookie + ("; Max-Age=0" if expire else "")

    def session(self, db, touch=False):
        key = self.session_key()
        now = int(time.time())
        row = run_db(db, "session_user", """SELECT u.id,u.username,u.name,u.role,s.last_seen,s.timeout
            FROM sessions s JOIN users u ON s.user_id=u.id
            WHERE s.token=? AND u.active=1""", (key,)).fetchone()
        if row is None or now - row["last_seen"] >= row["timeout"]:
            run_db(db, "session_remove", "DELETE FROM sessions WHERE token=?", (key,))
            raise Problem("Inicia sesión para continuar.", 401)
        if touch:
            run_db(db, "session_touch", "UPDATE sessions SET last_seen=? WHERE token=?", (now, key))
        return row

    def require(self, db, user, roles, path):
        if user["role"] not in roles:
            audit(db, user["username"], "ACCESO_DENEGADO", self.ip, path)
            raise Problem("Acceso denegado.", 403)

    def login(self, db):
        data = self.data()
        username = field(data, "username", 80).lower()
        password = data.get("password")
        if not isinstance(password, str) or not 1 <= len(password) <= 128:
            raise Problem("Usuario o contraseña incorrectos.", 401)
        now = int(time.time())
        token = secrets.token_urlsafe(32)
        error = None
        locked = 0
        with transaction(db):
            user = run_db(db, "user_by_username", "SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if user and user["active"] and user["locked_until"] > now:
                error = Problem("Cuenta bloqueada temporalmente.", 423)
            else:
                stored = user["password"] if user and user["password"] else None
                candidate = password_hash(password, stored.split(":")[0] if stored else "00" * 16)
                if not stored or not secrets.compare_digest(stored, candidate) or not user["active"]:
                    error = Problem("Usuario o contraseña incorrectos.", 401)
                    if user and user["active"] and stored:
                        failures = (0 if user["locked_until"] else user["failures"]) + 1
                        locked = now + 900 if failures >= 5 else 0
                        run_db(db, "user_failures", "UPDATE users SET failures=?,locked_until=? WHERE id=?",
                                   (failures, locked, user["id"]))
                        if locked:
                            audit(db, username, "CUENTA_BLOQUEADA", self.ip, "15 minutos")
                            error = Problem("Cuenta bloqueada temporalmente.", 423)
                else:
                    timeout = 900 if data.get("mobile") is True else 1800
                    run_db(db, "user_unlock", "UPDATE users SET failures=0,locked_until=0 WHERE id=?", (user["id"],))
                    run_db(db, "sessions_cleanup", "DELETE FROM sessions WHERE token=? OR last_seen + timeout <= ?",
                               (self.session_key(), now))
                    run_db(db, "session_add", "INSERT INTO sessions VALUES(?,?,?,?)",
                               (digest(token), user["id"], now, timeout))
                    audit(db, username, "INGRESO", self.ip)
        if error:
            if locked:
                status = send_email(os.environ.get("VILLALI_SECURITY_EMAIL"),
                                    "Villali · Cuenta bloqueada",
                                    f"La cuenta {username} se bloqueó durante 15 minutos tras cinco intentos fallidos.",
                                    f"lock-{user['id']}-{locked}")
                audit(db, username, "CORREO_BLOQUEO", self.ip, status)
            raise error
        return self.respond({"ok": True}, Set_Cookie=self.session_cookie(token))

    def activate(self, db):
        data = self.data()
        token = field(data, "token", 100)
        new_password = password_hash(valid_password(data.get("password")))
        with transaction(db):
            row = run_db(db, "invited_user", """SELECT u.id,u.username FROM invitations i JOIN users u ON u.id=i.user_id
                WHERE i.token=? AND i.expires>? AND u.active=1""",
                (digest(token), int(time.time()))).fetchone()
            if not row:
                raise Problem("La invitación caducó o ya se usó.", 404)
            run_db(db, "user_password", "UPDATE users SET password=?,failures=0,locked_until=0 WHERE id=?",
                       (new_password, row["id"]))
            run_db(db, "invitation_remove", "DELETE FROM invitations WHERE user_id=?", (row["id"],))
            run_db(db, "user_sessions_remove", "DELETE FROM sessions WHERE user_id=?", (row["id"],))
            audit(db, row["username"], "CLAVE_CONFIGURADA", self.ip)
        return self.respond({"ok": True})

    def api(self, db, method, path, query):
        if (method, path) == ("POST", "/api/login"):
            return self.login(db)
        if (method, path) == ("POST", "/api/activate"):
            return self.activate(db)
        user = self.session(db, touch=path != "/api/session")
        if (method, path) == ("GET", "/api/session"):
            return self.respond({**dict(user), "role_name": ROLES[user["role"]],
                                 "catalog": user["role"] in CATALOG,
                                 "inventory": user["role"] in INVENTORY,
                                 "remaining": user["timeout"] - (int(time.time()) - user["last_seen"])})
        if (method, path) == ("POST", "/api/activity"):
            return self.respond({"ok": True})
        if (method, path) == ("POST", "/api/logout"):
            run_db(db, "session_remove", "DELETE FROM sessions WHERE token=?", (self.session_key(),))
            return self.respond({"ok": True}, Set_Cookie=self.session_cookie("", expire=True))
        if path == "/api/users":
            self.require(db, user, {"02"}, path)
            return self.users(db, user, method)
        if (method, path) == ("POST", "/api/users/delete"):
            self.require(db, user, {"02"}, path)
            return self.delete_user(db, user)
        if (method, path) == ("GET", "/api/audit"):
            self.require(db, user, {"02"}, path)
            return self.respond([dict(row) for row in run_db(db, "audit_list", 
                "SELECT * FROM audit ORDER BY id DESC LIMIT 100")])
        if path == "/api/products":
            self.require(db, user, {"03"} if method == "POST" else CATALOG, path)
            return self.products(db, user, method, query)
        if (method, path) == ("GET", "/api/inventory"):
            self.require(db, user, INVENTORY, path)
            return self.inventory(db, query)
        if (method, path) == ("GET", "/api/template"):
            self.require(db, user, {"03"}, path)
            return self.respond(template(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                Content_Disposition='attachment; filename="inventario_inicial.xlsx"')
        if method == "POST" and path in {"/api/import/preview", "/api/import/confirm"}:
            self.require(db, user, {"03"}, path)
            return self.import_inventory(db, user, path, query)
        audit(db, user["username"], "ACCESO_DENEGADO", self.ip, path)
        raise Problem("Ruta fuera del alcance del Sprint 1.", 403)

    def users(self, db, actor, method):
        if method == "GET":
            rows = run_db(db, "users_list", """SELECT id,username,name,role,active,password IS NOT NULL AS configured,email
                FROM users LEFT JOIN user_contacts ON user_contacts.user_id=users.id ORDER BY username""")
            return self.respond({"users": [dict(row) for row in rows], "roles": ROLES})
        data = self.data()
        role = data.get("role")
        if not isinstance(role, str) or role not in ROLES:
            raise Problem("Selecciona un rol válido.")
        name = field(data, "name")
        email = data.get("email", "")
        if not isinstance(email, str) or len(email) > 254 or (email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
            raise Problem("Indica un correo electrónico válido.")
        user_id = data.get("id")
        if user_id is not None and type(user_id) is not int:
            raise Problem("Usuario inválido.")
        token = None
        with transaction(db):
            if user_id is None:
                username = field(data, "username", 80).lower()
                if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,79}", username):
                    raise Problem("Usa al menos dos letras, números, puntos, guiones o guiones bajos.")
                user_id = run_db(db, "user_add", "INSERT INTO users(username,name,role) VALUES(?,?,?) RETURNING id",
                                     (username, name, role)).fetchone()["id"]
                token = secrets.token_urlsafe(32)
                run_db(db, "invitation_add", "INSERT INTO invitations VALUES(?,?,?)",
                           (digest(token), user_id, int(time.time()) + 86400))
            else:
                row = run_db(db, "user_by_id", "SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
                if not row:
                    raise Problem("Usuario no encontrado.", 404)
                active = data.get("active") is True
                if user_id == actor["id"] and (role != "02" or not active):
                    raise Problem("Tu cuenta debe conservar su acceso de administrador.")
                run_db(db, "user_edit", "UPDATE users SET name=?,role=?,active=? WHERE id=?",
                           (name, role, int(active), user_id))
                if not active or row["role"] != role:
                    run_db(db, "user_sessions_remove", "DELETE FROM sessions WHERE user_id=?", (user_id,))
                if active and data.get("invite") is True:
                    token = secrets.token_urlsafe(32)
                    run_db(db, "invitation_remove", "DELETE FROM invitations WHERE user_id=?", (user_id,))
                    run_db(db, "invitation_add", "INSERT INTO invitations VALUES(?,?,?)",
                               (digest(token), user_id, int(time.time()) + 86400))
            if "email" in data:
                if email:
                    run_db(db, "contact_save", """INSERT INTO user_contacts VALUES(?,?)
                        ON CONFLICT(user_id) DO UPDATE SET email=excluded.email""", (user_id, email))
                else:
                    run_db(db, "contact_remove", "DELETE FROM user_contacts WHERE user_id=?", (user_id,))
            else:
                contact = run_db(db, "contact_get", "SELECT email FROM user_contacts WHERE user_id=?", (user_id,)).fetchone()
                email = contact["email"] if contact else ""
            audit(db, actor["username"], "USUARIO_GUARDADO", self.ip, str(user_id))
        invitation = f"{self.server.origin}/#invitar={token}" if token else None
        status = None
        if invitation:
            status = send_email(email, "Activa tu cuenta de Villali",
                                f"Configura tu contraseña con este enlace válido durante 24 horas:\n{invitation}",
                                f"invite-{digest(token)}")
            audit(db, actor["username"], "CORREO_INVITACION", self.ip, f"{user_id}: {status}")
        return self.respond({"ok": True, "invitation": invitation if status != "aceptado" else None,
                             "mail_status": status})

    def delete_user(self, db, actor):
        data = self.data()
        user_id = data.get("id")
        if type(user_id) is not int or not 0 < user_id < 2**63:
            raise Problem("Usuario inválido.")
        if user_id == actor["id"]:
            raise Problem("No puedes eliminar tu propia cuenta de administrador.", 403)
        with transaction(db):
            current = run_db(db, "user_by_id", "SELECT * FROM users WHERE id=?", (actor["id"],)).fetchone()
            if not current or not current["active"] or current["role"] != "02":
                raise Problem("Acceso denegado.", 403)
            target = run_db(db, "user_by_id", "SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not target or target["username"] != data.get("username"):
                raise Problem("La cuenta ya no está disponible. Actualiza la lista de usuarios.", 404)
            run_db(db, "user_sessions_remove", "DELETE FROM sessions WHERE user_id=?", (user_id,))
            run_db(db, "invitation_remove", "DELETE FROM invitations WHERE user_id=?", (user_id,))
            run_db(db, "contact_remove", "DELETE FROM user_contacts WHERE user_id=?", (user_id,))
            run_db(db, "user_remove", "DELETE FROM users WHERE id=?", (user_id,))
            audit(db, current["username"], "USUARIO_ELIMINADO", self.ip, f"{target['username']} (ID {user_id})")
        return self.respond({"ok": True})

    def products(self, db, actor, method, query):
        if method == "GET":
            search = query.get("q", [""])[0][:120]
            brand = query.get("brand", [""])[0][:120]
            species = query.get("species", [""])[0][:120]
            try:
                page = integer(query.get("page", ["1"])[0], 1)
            except ValueError:
                raise Problem("Página inválida.") from None
            pattern = f"%{search}%"
            rows = run_db(db, "catalog_page", """SELECT products.*,catalog_sources.price_status
                FROM products LEFT JOIN catalog_sources ON catalog_sources.product_id=products.id
                WHERE (active=1 OR ?=1)
                AND (LOWER(name) LIKE LOWER(?) OR LOWER(sku) LIKE LOWER(?) OR barcode LIKE ?)
                AND LOWER(brand) LIKE LOWER(?) AND LOWER(species) LIKE LOWER(?)
                ORDER BY name,id LIMIT 26 OFFSET ?""",
                (int(actor["role"] == "03"), pattern, pattern, pattern,
                 f"%{brand}%", f"%{species}%", (page - 1) * 25)).fetchall()
            return self.respond({"products": [dict(row) for row in rows[:25]], "more": len(rows) > 25})
        data = self.data()
        sku, barcode = field(data, "sku").upper(), field(data, "barcode")
        if not re.fullmatch(r"\d{13}", barcode):
            raise Problem("El código EAN-13 debe contener 13 dígitos.")
        product_id = data.get("id")
        if product_id is not None and type(product_id) is not int:
            raise Problem("Producto inválido.")
        source = run_db(db, "catalog_source", """SELECT price_status,presentation,price_cents
            FROM catalog_sources JOIN products ON products.id=product_id WHERE product_id=?""",
            (product_id,)).fetchone()
        price_missing = bool(source and source["price_status"] == "Pendiente de cotización"
                             and data.get("price") == "")
        presentation = "" if source and not source["presentation"] and data.get("presentation") == "" else field(data, "presentation")
        try:
            price = Decimal(0) if price_missing else Decimal(field(data, "price", 16))
            cents = price * 100
            if not cents.is_finite() or not 0 <= cents <= 10**14 or cents != cents.to_integral_value():
                raise ValueError
            minimum = integer(data.get("minimum"), 1)
        except (InvalidOperation, ValueError):
            raise Problem("Indica un precio válido y un stock mínimo entero mayor que cero.") from None
        values = (sku, barcode, field(data, "name"), field(data, "brand"), field(data, "species"),
                  presentation, int(cents), minimum)
        with transaction(db):
            current = run_db(db, "product_by_id", "SELECT sku FROM products WHERE id=?", (product_id,)).fetchone()
            old_sku = current["sku"] if current else ""
            if sku != old_sku and (sku.startswith("DEMO-IT-") or old_sku.startswith("DEMO-IT-")):
                raise Problem("Los SKU con prefijo DEMO-IT- están reservados para demostración.")
            existing = run_db(db, "product_by_barcode", "SELECT id,sku FROM products WHERE barcode=?", (barcode,)).fetchone()
            if existing and existing["id"] != product_id:
                raise Problem(f"Código de barras ya registrado en {existing['sku']}.", 409)
            if product_id is None:
                product_id = run_db(db, "product_add", """INSERT INTO products
                    (sku,barcode,name,brand,species,presentation,price_cents,minimum)
                    VALUES(?,?,?,?,?,?,?,?) RETURNING id""", values).fetchone()["id"]
            else:
                updated = run_db(db, "product_edit", """UPDATE products SET sku=?,barcode=?,name=?,brand=?,species=?,
                    presentation=?,price_cents=?,minimum=?,active=? WHERE id=?""",
                    (*values, int(data.get("active") is True), product_id))
                if not updated.rowcount:
                    raise Problem("Producto no encontrado.", 404)
                if source and not price_missing and (source["price_status"] == "Pendiente de cotización"
                                                     or source["price_cents"] != int(cents)):
                    run_db(db, "price_internal", """UPDATE catalog_sources SET price_status='Precio interno'
                        WHERE product_id=?""", (product_id,))
            audit(db, actor["username"], "PRODUCTO_GUARDADO", self.ip, sku)
        return self.respond({"ok": True, "id": product_id})

    def import_inventory(self, db, user, path, query):
        raw = self.body(4_000_000)
        checksum = hashlib.sha256(raw).hexdigest()
        if path.endswith("/preview"):
            rows, errors = inventory_rows(db, raw)
            return self.respond({"digest": checksum, "count": len(rows), "errors": errors,
                                 "units": sum(row[-1] for row in rows)})
        if query.get("digest") != [checksum]:
            raise Problem("El archivo cambió. Valídalo de nuevo.")
        with transaction(db):
            previous = run_db(db, "initial_import", "SELECT digest,row_count FROM imports WHERE id=1").fetchone()
            if previous:
                if previous["digest"] == checksum:
                    return self.respond({"ok": True, "count": previous["row_count"], "repeat": True})
                raise Problem("La bodega ya tiene una carga inicial.", 409)
            rows, errors = inventory_rows(db, raw)
            if errors:
                return self.respond({"error": "La importación fue rechazada.", "errors": errors}, 422)
            run_db(db, "lots_add", """INSERT INTO lots(product_id,lot,expiry,location,quantity)
                VALUES(?,?,?,?,?)""", rows)
            run_db(db, "import_add", "INSERT INTO imports VALUES(1,?,?)", (checksum, len(rows)))
            audit(db, user["username"], "CARGA_INICIAL", self.ip, f"{len(rows)} filas | {checksum}")
        return self.respond({"ok": True, "count": len(rows)})

    def inventory(self, db, query):
        barcode = query.get("code", [""])[0].strip()[:120]
        search = query.get("q", [""])[0].strip()[:120]
        real_inventory = int(run_db(db, "initial_import", "SELECT 1 FROM imports WHERE id=1").fetchone() is not None)
        if barcode:
            products = run_db(db, "inventory_by_barcode", """SELECT id,sku,name,barcode,species FROM products
                WHERE barcode=? AND active=1""", (barcode,)).fetchall()
        elif search:
            products = run_db(db, "inventory_search", """SELECT id,sku,name,barcode,species FROM products WHERE active=1
                AND LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 25""", (f"%{search}%",)).fetchall()
        else:
            products = run_db(db, "inventory_overview", """SELECT p.id,p.sku,p.name,p.barcode,p.species FROM products p
                WHERE p.active=1 AND EXISTS (SELECT 1 FROM lots l WHERE l.product_id=p.id
                AND (?=0 OR substr(l.lot,1,8) <> 'DEMO-IT-'))
                ORDER BY p.name,p.id LIMIT 25""", (real_inventory,)).fetchall()
        if not products and (barcode or search):
            raise Problem("Producto no registrado. Puedes buscar por nombre.", 404)
        if not products:
            return self.respond([])
        lots_by_product = {product["id"]: [] for product in products}
        placeholders = ",".join("?" for _ in lots_by_product)
        rows = run_db(db, "inventory_lots", f"""SELECT product_id,lot,expiry,location,quantity-reserved AS available
            FROM lots WHERE product_id IN ({placeholders})
            AND (?=0 OR substr(lot,1,8) <> 'DEMO-IT-')
            ORDER BY product_id,expiry,lot,location""", (*lots_by_product, real_inventory))
        today = date.today()
        for row in rows:
            lot = dict(row)
            product_id = lot.pop("product_id")
            days = (date.fromisoformat(lot["expiry"]) - today).days
            color = "rojo" if days <= 30 else "amarillo" if days <= 60 else "verde"
            lots_by_product[product_id].append({**lot, "days": days, "color": color,
                                                "demo": lot["lot"].startswith("DEMO-IT-")})
        result = []
        for product in products:
            lots = lots_by_product[product["id"]]
            result.append({**dict(product), "lots": lots, "total": sum(row["available"] for row in lots)})
        return self.respond(result)


def main():
    parser = argparse.ArgumentParser(description="Villali Sprint 1")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    parser.add_argument("--init-admin", action="store_true")
    parser.add_argument("--setup-if-needed", action="store_true")
    args = parser.parse_args()
    public_origin = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    if public_origin and (urlsplit(public_origin).scheme != "https" or not urlsplit(public_origin).hostname):
        parser.error("RENDER_EXTERNAL_URL debe ser HTTPS.")
    if public_origin and not (os.environ.get("MONGODB_URI") or os.environ.get("DATABASE_URL")):
        parser.error("Configura MONGODB_URI o DATABASE_URL para guardar los datos fuera de Render.")
    with database() as db:
        initialize_schema(db)
        has_admin = run_db(db, "active_admin", "SELECT 1 FROM users WHERE role='02' AND active=1").fetchone()
        if args.init_admin and has_admin:
            parser.error("Ya existe un administrador activo.")
        if not has_admin and public_origin:
            try:
                password = valid_password(os.environ.get("VILLALI_ADMIN_PASSWORD"))
            except Problem as error:
                parser.error(f"Configura VILLALI_ADMIN_PASSWORD. {error}")
            with transaction(db):
                if not run_db(db, "active_admin", "SELECT 1 FROM users WHERE role='02' AND active=1").fetchone():
                    run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                               ("admin", "Administrador", password_hash(password), "02"))
            has_admin = True
        if not has_admin and (args.init_admin or args.setup_if_needed):
            print("Primer arranque. El usuario es admin. Crea una contraseña nueva.")
            print("Usa 10 a 128 caracteres con mayúscula, número y símbolo.")
            while True:
                try:
                    password = valid_password(getpass("Nueva contraseña para admin: "))
                    if getpass("Repite la contraseña: ") != password:
                        raise Problem("Las contraseñas no coinciden.")
                except Problem as error:
                    print(f"{error} Inténtalo de nuevo.")
                except (EOFError, KeyboardInterrupt):
                    print("\nConfiguración cancelada.")
                    return
                else:
                    break
            with transaction(db):
                if run_db(db, "active_admin", "SELECT 1 FROM users WHERE role='02' AND active=1").fetchone():
                    parser.error("Ya existe un administrador activo.")
                run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                           ("admin", "Administrador", password_hash(password), "02"))
            print("Administrador creado. Usuario: admin")
            has_admin = True
            if args.init_admin:
                return
        if not has_admin:
            parser.error("Ejecuta primero app.py --init-admin.")
    server = ThreadingHTTPServer(("0.0.0.0" if public_origin else "127.0.0.1", args.port), Handler)
    server.origin = public_origin or f"http://localhost:{server.server_port}"
    print(f"Villali Sprint 1 · {server.origin}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
