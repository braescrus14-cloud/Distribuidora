from datetime import date, timedelta
from hashlib import sha256
from http.client import HTTPConnection
from io import BytesIO
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import time

from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app
import demo_italcol


def excel(sku):
    book = Workbook()
    book.active.append(app.HEADERS)
    book.active.append((sku, "L-115", date.today() + timedelta(days=150), 60, "B1"))
    book.active.append(("CHK-CAC-15", "L-101", date.today() + timedelta(days=20), 40, "A1"))
    out = BytesIO()
    book.save(out)
    return out.getvalue()


with TemporaryDirectory() as directory:
    app.DB = Path(directory) / "test.sqlite3"
    password = "Prueba!2026"
    with app.database() as db:
        app.initialize_schema(db)
        app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                   ("admin", "Admin", app.password_hash(password), "02"))
    assert demo_italcol.seed() == (24, 72)
    assert demo_italcol.seed() == (0, 0)
    messages = []
    os.environ["VILLALI_SECURITY_EMAIL"] = "seguridad@example.test"

    def fake_email(recipient, subject, message, event_key):
        if not recipient:
            return "sin_configurar"
        messages.append((recipient, subject, message, event_key))
        return "aceptado"

    app.send_email = fake_email
    server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    host = f"localhost:{server.server_port}"
    server.origin = "http://" + host
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def call(path, status=200, data=None, cookie="", origin=True, decode=True):
        headers = {"Host": host}
        if cookie:
            headers["Cookie"] = cookie
        if origin:
            headers["Origin"] = server.origin
        if data is not None and not isinstance(data, bytes):
            headers["Content-Type"] = "application/json"
            data = json.dumps(data)
        connection = HTTPConnection("127.0.0.1", server.server_port)
        try:
            connection.request("GET" if data is None else "POST", path, data, headers)
            response = connection.getresponse()
            raw = response.read()
            assert response.status == status, (path, response.status, raw)
            return json.loads(raw) if decode else raw, response.getheader("Set-Cookie", "").split(";")[0]
        finally:
            connection.close()

    def login(username, expected=200, mobile=False):
        return call("/api/login", expected,
                    {"username": username, "password": password, "mobile": mobile})[1]

    try:
        assert b"Villali" in call("/", decode=False)[0]
        assert call("/health")[0] == {"status": "ok"}
        call("/api/session", 401)
        call("/api/login", 403, {"username": "admin", "password": password}, origin=False)
        admin = login("admin")
        users = {}
        for role, name in (("03", "jefe"), ("04", "aux")):
            result = call("/api/users", data={"username": name, "name": name, "role": role,
                          "email": "jefe@example.test" if role == "03" else ""}, cookie=admin)[0]
            listed = next(row for row in call("/api/users", cookie=admin)[0]["users"] if row["username"] == name)
            assert result["account"] == {**listed, "email": listed["email"] or ""}
            if role == "03":
                assert result["mail_status"] == "aceptado" and not result["invitation"]
                assert messages[-1][0] == "jefe@example.test"
                invitation = messages[-1][2].splitlines()[-1]
            else:
                assert result["mail_status"] == "sin_configurar"
                invitation = result["invitation"]
            token = invitation.split("=")[-1]
            call("/api/activate", data={"token": token, "password": password})
            call("/api/activate", 404, {"token": token, "password": password})
            users[name] = login(name, mobile=name == "aux")
        boss, aux = users["jefe"], users["aux"]
        overview = call("/api/inventory", cookie=aux)[0]
        assert len(overview) == 24
        assert sum(len(product["lots"]) for product in overview) == 72
        assert all(lot["demo"] for product in overview for lot in product["lots"])
        assert any(row["name"] == "Aquatilapia 30" for row in call("/api/inventory?q=Aquatilapia", cookie=aux)[0])
        assert call("/api/session", cookie=aux)[0]["timeout"] == 900
        assert call("/api/session", cookie=admin)[0]["timeout"] == 1800
        call("/api/users", 403, cookie=aux)
        call("/api/facturacion", 403, cookie=aux)
        product = {"sku": "CHK-CAC-15", "barcode": "7702001234567", "name": "Chunky Cachorros 15 kg",
                   "brand": "Chunky", "species": "Caninos", "presentation": "15 kg", "price": "185000", "minimum": 10}
        call("/api/products", 403, product, aux)
        call("/api/products", data=product, cookie=boss)
        assert "CHK-CAC-15" in call("/api/products", 409, {**product, "sku": "OTRO"}, boss)[0]["error"]
        assert len(call("/api/products?species=Caninos&brand=Chunky", cookie=boss)[0]["products"]) == 1
        raw = call("/api/template", cookie=boss, decode=False)[0]
        assert tuple(next(load_workbook(BytesIO(raw)).active.values)) == app.HEADERS
        invalid = excel("NO-EXISTE")
        valid = excel("CHK-CAC-15")
        errors = call("/api/import/preview", data=invalid, cookie=boss)[0]["errors"]
        assert [item["fila"] for item in errors] == [2]
        call("/api/import/confirm?digest=" + sha256(invalid).hexdigest(), 422, invalid, boss)
        assert call("/api/inventory?code=7702001234567", cookie=aux)[0][0]["total"] == 0
        preview = call("/api/import/preview", data=valid, cookie=boss)[0]
        assert preview["count"] == 2 and preview["units"] == 100 and not preview["errors"]
        target = "/api/import/confirm?digest=" + preview["digest"]
        assert call(target, data=valid, cookie=boss)[0]["count"] == 2
        assert [item["sku"] for item in call("/api/inventory", cookie=aux)[0]] == ["CHK-CAC-15"]
        assert call(target, data=valid, cookie=boss)[0]["repeat"]
        call("/api/import/confirm?digest=" + sha256(invalid).hexdigest(), 409, invalid, boss)
        results = call("/api/inventory?code=7702001234567", cookie=aux)[0][0]
        assert results["total"] == 100
        assert [(lot["lot"], lot["color"]) for lot in results["lots"]] == [("L-101", "rojo"), ("L-115", "verde")]
        call("/api/inventory?code=999", 404, cookie=aux)
        assert call("/api/inventory?q=Chunky", cookie=aux)[0][0]["sku"] == "CHK-CAC-15"
        with app.database() as db:
            if hasattr(db, "run"):
                db.update("lots", {"lot": "L-101"}, {"reserved": 10})
            else:
                db.execute("UPDATE lots SET reserved=10 WHERE lot='L-101'")
        assert call("/api/inventory?code=7702001234567", cookie=aux)[0][0]["lots"][0]["available"] == 30
        with app.database() as db:
            app.run_db(db, "session_touch", "UPDATE sessions SET last_seen=? WHERE token=?",
                       (int(time.time()) - 900, app.digest(aux.split("=")[1])))
        call("/api/inventory?q=Chunky", 401, cookie=aux)
        for attempt in range(5):
            call("/api/login", 423 if attempt == 4 else 401, {"username": "aux", "password": "Incorrecta"})
        login("aux", 423)
        assert len(messages) == 2 and messages[-1][0] == "seguridad@example.test"
        assert "aux" in messages[-1][2] and messages[-1][3].startswith("lock-")
        entries = call("/api/audit", cookie=admin)[0]
        assert {"ACCESO_DENEGADO", "CARGA_INICIAL", "CUENTA_BLOQUEADA", "INGRESO"} <= {entry["event"] for entry in entries}
        records = call("/api/users", cookie=admin)[0]["users"]
        chief = next(row for row in records if row["username"] == "jefe")
        updated = call("/api/users", data={"id": chief["id"], "name": chief["name"],
                       "role": chief["role"], "active": False}, cookie=admin)[0]["account"]
        assert updated == {**chief, "active": False}
        call("/api/session", 401, cookie=boss)
        login("jefe", 401)
        root = next(row for row in records if row["username"] == "admin")
        deletion = {"id": chief["id"], "username": "jefe"}
        call("/api/users/delete", 403, deletion, admin, origin=False)
        call("/api/users/delete", 401, deletion)
        call("/api/users/delete", 403, {"id": root["id"], "username": "admin"}, admin)
        call("/api/users/delete", 404, {**deletion, "username": "otro"}, admin)
        renewed = call("/api/users", data={**deletion, "name": chief["name"], "role": chief["role"],
                        "active": True, "invite": True}, cookie=admin)[0]
        assert renewed["mail_status"] == "aceptado"
        token = messages[-1][2].splitlines()[-1].split("=")[-1]
        boss = login("jefe")
        call("/api/users/delete", 403, deletion, boss)
        call("/api/users/delete", data=deletion, cookie=admin)
        call("/api/users/delete", 404, deletion, admin)
        call("/api/session", 401, cookie=boss)
        call("/api/activate", 404, {"token": token, "password": password})
        login("jefe", 401)
        remaining = call("/api/users", cookie=admin)[0]["users"]
        assert {row["username"] for row in remaining} == {"admin", "aux"}
        assert any(row["event"] == "USUARIO_ELIMINADO" and row["actor"] == "admin" and "jefe" in row["detail"]
                   for row in call("/api/audit", cookie=admin)[0])
        call("/api/logout", data={}, cookie=admin)
        call("/api/session", 401, cookie=admin)
        print("Flujo HTTP verificado para HU-01 a HU-05")
    finally:
        server.shutdown()
        worker.join()
        server.server_close()
