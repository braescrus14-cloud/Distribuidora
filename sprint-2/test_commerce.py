import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
from uuid import uuid4
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import app
from commerce import COLOMBIA
from commerce_seed import seed


def check():
    password = "Comercio!2026"
    names = {"01": "gerente", "03": "bodega", "05": "compras", "06": "asesor", "10": "cliente"}
    with app.database() as db:
        app.initialize_schema(db)
        for role, name in names.items():
            app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                       (name, name, app.password_hash(password), role))
        seed(db)
        seed(db)
    server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    host = f"localhost:{server.server_port}"
    server.origin = f"http://{host}"
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()

    def call(path, data=None, cookie="", status=200):
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=10)
        try:
            headers = {"Host": host, "Cookie": cookie, "Origin": server.origin, "Content-Type": "application/json"}
            conn.request("GET" if data is None else "POST", path,
                         None if data is None else json.dumps(data), headers)
            response = conn.getresponse()
            body = json.loads(response.read())
            if isinstance(status, tuple):
                assert response.status in status, (path, response.status, body)
                return response.status
            assert response.status == status, (path, response.status, body)
            return body, response.getheader("Set-Cookie", "").split(";")[0]
        finally:
            conn.close()

    def api(kind, role, data=None, status=200):
        result = call("/api/comercio/" + kind, data, cookies[role], status)
        return result[0] if isinstance(result, tuple) else result

    def order(sku="VIL-CAN-15", quantity=20, **kwargs):
        return {"action": "create", "request_id": str(uuid4()),
                "lines": [{"sku": sku, "quantity": quantity, "cost": 125000}], **kwargs}

    try:
        cookies = {role: call("/api/login", {"username": user, "password": password})[1]
                   for role, user in names.items()}
        vendors = api("proveedores", "05")
        assert len(vendors["rows"]) == 2
        vendor = next(row for row in vendors["rows"] if "VIL-CAN-15" in row["skus"])
        api("proveedores", "05", {**vendor, "nit": "900123456-0"}, 400)
        api("proveedores", "10", status=403)
        api("proveedores", "05", {**vendor, "nit": vendor["id"], "active": False})
        assert vendor["id"] not in [row["id"] for row in api("compras", "05")["suppliers"]]
        api("compras", "05", order(supplier=vendor["id"]), 400)
        api("proveedores", "05", {**vendor, "nit": vendor["id"]})

        submitted = order(quantity=100, supplier=vendor["id"])
        purchase = api("compras", "05", submitted)
        assert purchase["status"] == "Pendiente de aprobación"
        assert api("compras", "05", submitted)["id"] == purchase["id"]
        assert any(row["id"] == purchase["id"] for row in api("compras", "01")["rows"])
        api("compras", "05", {"action": "approve", "id": purchase["id"]}, 403)
        api("compras", "01", {"action": "approve", "id": purchase["id"]})
        today = datetime.now(COLOMBIA).date()
        receipt = {"id": purchase["id"], "action": "receive", "request_id": str(uuid4()),
                   "sku": "VIL-CAN-15", "lot": "CAN-778", "location": "A1", "quantity": 10}
        api("compras", "03", {**receipt, "expiry": str(today + timedelta(days=100))}, 400)
        ready = {**receipt, "expiry": str(today + timedelta(days=300))}
        assert api("compras", "03", ready)["status"] == "Recibida parcial"
        assert api("compras", "03", ready)["lines"][0]["received"] == 10
        assert api("compras", "03", {**ready, "request_id": str(uuid4()), "quantity": 90,
                                     "sku": "2050000001017"})["status"] == "Recibida completa"

        customer = api("clientes", "06", {"name": "Comercial Hacienda", "zone": "Norte", "type": "mayorista",
                                          "account": 0, "active": True, "consent": True})
        assert customer["price_list"] == "A" and customer["credit"] == 0
        api("clientes", "06", {"id": customer["id"], "credit": 10}, 403)
        api("clientes", "01", {"id": customer["id"], "credit": 300_000_000, "balance": 0})
        denied = api("pedidos", "06", order(customer="monte-claro", credit=True), 409)
        assert "cartera vencida" in denied["error"]
        api("pedidos", "06", order(quantity=151, customer=customer["id"]), 409)
        portal = api("pedidos", "10")
        assert len(portal["customers"]) == 1 and portal["customers"][0]["id"] == "alto-verde"
        assert any(row["sku"] == "VIL-AVI-40" and row["available"] == 0 for row in portal["products"])
        call("/api/products", cookie=cookies["10"], status=403)
        pending = api("pedidos", "10", order())
        assert pending["status"] == "PENDIENTE_REVISIÓN"
        confirmed = api("pedidos", "06", {"action": "confirm", "id": pending["id"]})
        assert confirmed["status"] == "CONFIRMADO"
        assert confirmed["lines"][0]["price"] == 9_262_500
        assert sum(row["quantity"] for row in confirmed["lines"][0]["reservations"]) == 20
        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: api("pedidos", "06",
                            order(quantity=100, customer=customer["id"]), (200, 409)), range(2)))
        assert sorted(statuses) == [200, 409]
        stock = api("pedidos", "06")["products"]
        assert next(item["available"] for item in stock if item["sku"] == "VIL-CAN-15") == 30
        print("HU-06 a HU-10 verificadas en HTTP, incluida la reserva concurrente.")
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


with tempfile.TemporaryDirectory() as temporary:
    app.DB = Path(temporary) / "commerce.sqlite3"
    check()
