"""Integration checks for public requests, recovery, contact privacy and durable storage."""
import json
import re
import tempfile
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from uuid import uuid4

import app
import public_portal


def check():
    password = "Publico!2026"
    with app.database() as db:
        app.initialize_schema(db)
        for name, role in (("portaladmin", "02"), ("portalcliente", "10")):
            app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                       (name, name, app.password_hash(password), role))
        user = app.run_db(db, "user_by_username", "SELECT * FROM users WHERE username=?", ("portalcliente",)).fetchone()
        app.run_db(db, "contact_save", "INSERT INTO user_contacts VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET email=excluded.email",
                   (user["id"], "cliente@example.com"))
    mails = []
    original_mail = public_portal.send_email
    public_portal.send_email = lambda *args: mails.append(args) or "aceptado"
    server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    server.origin = "http://localhost:" + str(server.server_port)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def call(path, data=None, cookie="", expected=200, origin=None):
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=15)
        try:
            connection.request("POST" if data is not None else "GET", path, json.dumps(data) if data is not None else None,
                {"Host": "localhost:" + str(server.server_port), "Origin": origin or server.origin,
                 "Content-Type": "application/json", "Cookie": cookie})
            response = connection.getresponse()
            raw = response.read()
            assert response.status == expected, (path, expected, response.status, raw[:200])
            body = json.loads(raw) if "application/json" in response.getheader("Content-Type", "") else raw
            return body, response.getheader("Set-Cookie", "").split(";")[0], response.getheader("X-Robots-Tag")
        finally:
            connection.close()

    try:
        admin = call("/api/login", {"username": "portaladmin", "password": password})[1]
        customer = call("/api/login", {"username": "portalcliente", "password": password, "audience": "cliente"})[1]
        call("/api/login", {"username": "portaladmin", "password": password, "audience": "cliente"})
        call("/api/login", {"username": "CLIENTE@example.com", "password": password})
        assert call("/")[2] is None and b'name="robots"' not in call("/")[0]
        assert b"Allow: /" in call("/robots.txt")[0] and b"Disallow: /\n" not in call("/robots.txt")[0]
        assert "noindex" in call("/entrar")[2]
        with app.database() as db:
            administrator = app.run_db(db, "user_by_username", "SELECT * FROM users WHERE username=?", ("portaladmin",)).fetchone()
            app.run_db(db, "contact_save", "INSERT INTO user_contacts VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET email=excluded.email", (administrator["id"], "cliente@example.com"))
        call("/api/login", {"username":"cliente@example.com", "password":password}, expected=401)
        with app.database() as db:
            app.run_db(db, "contact_remove", "DELETE FROM user_contacts WHERE user_id=?", (administrator["id"],))
        assert "phone" in call("/api/public/contact")[0]
        call("/api/public-admin/requests", expected=401)
        call("/api/public-admin/requests", cookie=customer, expected=403)
        contact = {"phone": "+573001234567", "email": "contacto@example.com", "legal_name": "Empresa de ensayo",
                   "nit": "", "address": "", "hours": "Lunes a viernes"}
        call("/api/public-admin/contact", contact, customer, expected=403)
        call("/api/public-admin/contact", contact, admin)
        assert all(call("/api/public/contact")[0][key] == value for key,value in contact.items() if value)
        call("/api/public-admin/contact", {"facebook_url":"javascript:alert(1)"}, admin, expected=400)
        call("/api/public-admin/contact", {"testimonial_1_approved":"yes"}, admin, expected=400)
        draft = {"testimonial_1_quote":"Testimonio de ensayo", "testimonial_1_name":"Productor de ensayo", "testimonial_1_farm":"Finca de ensayo", "testimonial_1_municipality":"Municipio de ensayo"}
        call("/api/public-admin/contact", draft, admin)
        assert call("/api/public/contact")[0]["testimonial_1_quote"] == ""
        assert call("/api/public-admin/contact", cookie=admin)[0]["testimonial_1_quote"] == draft["testimonial_1_quote"]
        call("/api/public-admin/contact", {"testimonial_1_approved":"yes"}, admin)
        assert call("/api/public/contact")[0]["testimonial_1_quote"] == draft["testimonial_1_quote"]
        call("/api/public-admin/contact", {"testimonial_1_approved":""}, admin)
        assert call("/api/public/contact")[0]["testimonial_1_quote"] == ""
        call("/api/public-admin/contact", {"city":"Ciudad de ensayo","response_time":"Tiempo de ensayo","stat_years":"2"}, admin)
        public = call("/api/public/contact")[0]
        assert public["phone"] == contact["phone"] and public["city"] == "Ciudad de ensayo" and public["stat_years"] == "2"
        # The website field is a trap, never a producer requirement.
        call("/api/public/account-requests", {"website":"https://spam.example"})
        assert call("/api/public-admin/requests", cookie=admin)[0] == []
        request = {"name": "Productor de ensayo", "email": "productor@example.com", "phone": "+57 300 999 8877",
                   "farm": "Finca de ensayo", "interest": "Avicultura", "consent": True, "request_id": str(uuid4())}
        call("/api/public/account-requests", {**request, "consent": False}, expected=400)
        call("/api/public/account-requests", request, origin="https://otro.example", expected=403)
        call("/api/public/account-requests", request)
        call("/api/public/account-requests", request)
        rows = call("/api/public-admin/requests", cookie=admin)[0]
        assert len(rows) == 1 and rows[0]["status"] == "PENDIENTE"
        call("/api/public-admin/requests", {"id": request["request_id"], "status": "CONTACTADO"}, admin)
        assert call("/api/public-admin/requests", cookie=admin)[0][0]["status"] == "CONTACTADO"
        # Rate limiting is transactional and does not affect the recovery bucket.
        for _ in range(7):
            call("/api/public/account-requests", {**request, "request_id": str(uuid4())})
        call("/api/public/account-requests", {**request, "request_id": str(uuid4())}, expected=429)
        unknown = call("/api/public/recover", {"username": "inexistente", "email": "nadie@example.com"})[0]
        known = call("/api/public/recover", {"username": "portalcliente", "email": "cliente@example.com"})[0]
        assert unknown == known and len(mails) == 1
        token = re.search(r"invitar=([A-Za-z0-9_-]+)", mails[0][2]).group(1)
        # Asking for a recovery link does not change the password or reveal the token in the response.
        assert token not in json.dumps(known)
        call("/api/login", {"username": "portalcliente", "password": password})
        call("/api/activate", {"token": token, "password": "Recuperada!2026"})
        call("/api/activate", {"token": token, "password": "Recuperada!2026"}, expected=404)
        call("/api/session", cookie=customer, expected=401)
        call("/api/login", {"username": "portalcliente", "password": "Recuperada!2026"})
        server.shutdown(); server.server_close(); thread.join()
        with app.database() as db:
            app.initialize_schema(db)
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        server.origin = "http://localhost:" + str(server.server_port)
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        assert len(call("/api/public-admin/requests", cookie=admin)[0]) == 8
        assert call("/api/public/contact")[0]["phone"] == contact["phone"]
        import os
        previous = os.environ.get("VILLALI_SITE_MODE")
        try:
            os.environ["VILLALI_SITE_MODE"] = "production"
            assert call("/")[2] is None and b'name="robots"' not in call("/")[0]
            assert "noindex" in call("/entrar")[2] and b'noindex' in call("/entrar")[0]
            assert b'Allow: /' in call("/robots.txt")[0] and b'Disallow: /entrar' not in call("/robots.txt")[0]
        finally:
            if previous is None: os.environ.pop("VILLALI_SITE_MODE", None)
            else: os.environ["VILLALI_SITE_MODE"] = previous
        print("Portada: solicitudes persistentes, permisos, consentimiento, límite de envíos y recuperación de un solo uso OK.")
    finally:
        public_portal.send_email = original_mail
        server.shutdown(); server.server_close(); thread.join()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporary:
        app.DB = Path(temporary) / "public.sqlite3"
        check()
