"""Authentication audit against a disposable database; never uses real credentials."""
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import secrets
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


def check():
    passwords = {role: f"Acceso!2026-{role}" for role in app.ROLES}
    with app.database() as db:
        app.initialize_schema(db)
        for role, password in passwords.items():
            hashed = app.password_hash(password)
            assert hashed != password and app.password_hash(password) != hashed
            app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                       ("audit-"+role, "Auditoría "+role, hashed, role))
    for value in (None, "admin", "a"*10, "A123456789", "A!"+"x"*8, "A1!"+"x"*126):
        try:
            app.valid_password(value)
        except app.Problem:
            pass
        else:
            raise AssertionError("A weak or oversized password was accepted")
    assert app.valid_password("A1!"+"x"*125)
    server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    server.origin = f"http://localhost:{server.server_port}"
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def call(path, data=None, cookie="", status=200, origin=None):
        headers = {"Host": f"localhost:{server.server_port}", "Content-Type": "application/json",
                   "Origin": origin or server.origin, "Cookie": cookie}
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=20)
        try:
            connection.request("POST" if data is not None else "GET", path,
                               json.dumps(data).encode() if data is not None else None, headers)
            response = connection.getresponse()
            raw = response.read()
            assert response.status == status, (path, status, response.status, raw[:200])
            return json.loads(raw), response.getheader("Set-Cookie", "")
        finally:
            connection.close()

    def login(role, password=None, **extra):
        return call("/api/login", {"username": "AUDIT-"+role, "password": password or passwords[role], **extra})[1].split(";")[0]

    try:
        assert call("/version")[0]["sprints"] == [1, 2, 3, 4]
        call("/api/session", status=401)
        call("/api/login", {"username": "audit-02", "password": passwords["02"]}, status=403, origin="https://otra-web.example")
        cookies = {}
        for role in app.ROLES:
            cookie = login(role, mobile=role == "08")
            cookies[role] = cookie
            user = call("/api/session", cookie=cookie)[0]
            assert user["role"] == role and user["username"] == "audit-"+role
            assert "password" not in user and "token" not in user
            call("/api/login", {"username": "audit-"+role, "password": passwords["01" if role != "01" else "02"]}, status=401)
            call("/api/users", cookie=cookie, status=200 if role == "02" else 403)
            call("/api/inventory", cookie=cookie, status=200 if role in app.INVENTORY else 403)
            call("/api/products", cookie=cookie, status=200 if role in app.CATALOG - {"10"} else 403)
            assert user["timeout"] == (900 if role == "08" else 1800)
        admin = cookies["02"]
        users = call("/api/users", cookie=admin)[0]["users"]
        assert all("password" not in row and "token" not in row for row in users)
        target = next(r for r in users if r["username"] == "audit-04")
        call("/api/users", {"id": target["id"], "name": target["name"], "role": "04", "active": False}, admin)
        call("/api/session", cookie=cookies["04"], status=401)
        call("/api/login", {"username": "audit-04", "password": passwords["04"]}, status=401)
        call("/api/users", {"id": target["id"], "name": target["name"], "role": "06", "active": True}, admin)
        changed = login("04")
        assert call("/api/session", cookie=changed)[0]["role"] == "06"
        call("/api/inventory", cookie=changed, status=403)
        with app.database() as db:
            app.run_db(db, "session_touch", "UPDATE sessions SET last_seen=? WHERE token=?",
                       (int(time.time())-1800, app.digest(changed.split("=", 1)[1])))
        call("/api/session", cookie=changed, status=401)
        token = secrets.token_urlsafe(32)
        with app.database() as db:
            app.run_db(db, "invitation_add", "INSERT INTO invitations VALUES(?,?,?)",
                       (app.digest(token), target["id"], int(time.time())-1))
        call("/api/activate", {"token": token, "password": "Nueva!2026"}, status=404)
        active = login("04")
        with app.database() as db:
            app.run_db(db, "invitation_remove", "DELETE FROM invitations WHERE user_id=?", (target["id"],))
            app.run_db(db, "invitation_add", "INSERT INTO invitations VALUES(?,?,?)",
                       (app.digest(token), target["id"], int(time.time())+60))
        call("/api/activate", {"token": token, "password": "Nueva!2026"})
        call("/api/session", cookie=active, status=401)
        call("/api/activate", {"token": token, "password": "Nueva!2026"}, status=404)
        call("/api/login", {"username": "audit-04", "password": passwords["04"]}, status=401)
        login("04", "Nueva!2026")
        secure = server.origin
        server.origin = "https://localhost:"+str(server.server_port)
        try:
            _, header = call("/api/login", {"username": "audit-02", "password": passwords["02"]})
            assert "HttpOnly" in header and "SameSite=Strict" in header and "; Secure" in header
        finally:
            server.origin = secure
        call("/api/logout", {}, admin)
        call("/api/session", cookie=admin, status=401)
        print("Access PASS: ten distinct passwords, role permissions, cookie flags, expired/reused activation, session revocation, role change, inactivity and logout.")
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        app.DB = Path(directory) / "access.sqlite3"
        check()
