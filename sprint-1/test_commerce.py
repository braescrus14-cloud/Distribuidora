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
    names = {"01": "gerente", "02": "admin", "03": "bodega", "05": "compras",
             "06": "asesor", "10": "cliente", "otro": "cliente.segundo"}
    with app.database() as db:
        app.initialize_schema(db)
        for role, name in names.items():
            app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                       (name, name, app.password_hash(password), "10" if role == "otro" else role))
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
        api("compras", "03", {**ready, "request_id": str(uuid4()), "quantity": 91}, 400)
        api("compras", "03", {**ready, "request_id": str(uuid4()), "location": "A2",
                             "expiry": str(today + timedelta(days=301))}, 409)
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
        assert portal["portal"]["name"] == "Agropecuaria Alto Verde" and "customers" not in portal
        assert any(row["sku"] == "VIL-AVI-40" and row["available"] == 0 for row in portal["products"])
        call("/api/products", cookie=cookies["10"], status=403)
        assert api("pedidos", "otro") == {"rows": [], "products": [], "portal": None}
        api("pedidos", "10", order(customer=customer["id"]), 403)
        api("pedidos", "otro", order(), 403)
        pending = api("pedidos", "10", order())
        assert pending["status"] == "PENDIENTE_REVISIÓN"
        account = next(row["id"] for row in api("clientes", "06")["accounts"] if row["name"] == "cliente.segundo")
        api("clientes", "06", {"id": customer["id"], "name": customer["name"], "zone": customer["zone"],
                               "type": customer["type"], "account": account, "active": True, "consent": True})
        assert api("pedidos", "otro")["rows"] == []
        other_order = api("pedidos", "otro", order(quantity=1))
        assert [row["number"] for row in api("pedidos", "10")["rows"]] == [pending["number"]]
        assert [row["number"] for row in api("pedidos", "otro")["rows"]] == [other_order["number"]]
        order_id = next(row["id"] for row in api("pedidos", "06")["rows"] if row["number"] == pending["number"])
        confirmed = api("pedidos", "06", {"action": "confirm", "id": order_id})
        assert confirmed["status"] == "CONFIRMADO"
        assert confirmed["lines"][0]["price"] == 9_262_500
        assert sum(row["quantity"] for row in confirmed["lines"][0]["reservations"]) == 20
        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: api("pedidos", "06",
                            order(quantity=100, customer=customer["id"]), (200, 409)), range(2)))
        assert sorted(statuses) == [200, 409]
        stock = api("pedidos", "06")["products"]
        assert next(item["available"] for item in stock if item["sku"] == "VIL-CAN-15") == 30
        api("practica", "10", status=403)
        api("practica", "05", {}, status=403)
        assert api("practica", "02", {}) == {"products": 3, "lots": 6}
        assert api("practica", "03", {}) == {"products": 3, "lots": 6}
        practice = api("practica", "05")
        assert len({lot["expiry"] for row in practice for lot in row["lots"]}) > 2
        assert api("pedidos", "06")["products"] == stock
        call("/api/users/delete", {"id": account, "username": "cliente.segundo"}, cookies["02"])
        updated = next(row for row in api("clientes", "06")["rows"] if row["id"] == customer["id"])
        assert updated["account"] == 0
        server.shutdown()
        server.server_close()
        worker.join()

        with app.database() as db:
            app.initialize_schema(db)
            seed(db)
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        host = f"localhost:{server.server_port}"
        server.origin = f"http://{host}"
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        assert any(row["id"] == vendor["id"] for row in api("proveedores", "05")["rows"])
        assert any(row["id"] == customer["id"] for row in api("clientes", "06")["rows"])
        assert any(row["id"] == purchase["id"] and row["status"] == "Recibida completa"
                   for row in api("compras", "03")["rows"])
        persisted = api("pedidos", "06")
        assert any(row["id"] == confirmed["id"] and row["status"] == "CONFIRMADO" for row in persisted["rows"])
        assert next(item["available"] for item in persisted["products"] if item["sku"] == "VIL-CAN-15") == 30
        print("HU-06 a HU-10 verificadas en HTTP, incluida la persistencia tras reiniciar el servidor.")
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


with tempfile.TemporaryDirectory() as temporary:
    app.DB = Path(temporary) / "commerce.sqlite3"
    check()
