"""Sprint 3 integration: HTTP authorization, FEFO, atomic stock, dispatch and proof."""
import base64
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from http.client import HTTPConnection
from io import BytesIO
from pathlib import Path
from threading import Thread
from uuid import uuid4

import app
from commerce import COLOMBIA, products, save
from commerce_seed import seed


def check():
    password = "Logistica!2026"
    names = {f"{i:02}": "perfil" + str(i) for i in range(1, 11)}
    names["otro"] = "otrocliente"
    names["driver2"] = "otroconductor"
    with app.database() as db:
        app.initialize_schema(db)
        for role, name in names.items():
            app.run_db(db, "admin_add", "INSERT INTO users(username,name,password,role) VALUES(?,?,?,?)",
                       (name, name, app.password_hash(password), {"otro": "10", "driver2": "08"}.get(role, role)))
        seed(db)
        product = products(db)["VIL-CAN-15"]
        app.run_db(db, "commerce_lot_add", "INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved) VALUES(?,?,?,?,?,?)",
                   (product["id"], "FEFO-PRIMERO", str(datetime.now(COLOMBIA).date() + timedelta(days=90)), "A1", 10, 0))
    server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)

    def start():
        server.origin = f"http://localhost:{server.server_port}"
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        return worker

    worker = start()

    def call(path, role=None, data=None, status=200):
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=20)
        try:
            connection.request("POST" if data is not None else "GET", path,
                json.dumps(data) if data is not None else None,
                {"Host": f"localhost:{server.server_port}", "Origin": server.origin,
                 "Cookie": cookies[role] if role else "", "Content-Type": "application/json"})
            response = connection.getresponse()
            raw = response.read()
            result = json.loads(raw) if "application/json" in response.getheader("Content-Type", "") else raw
            assert response.status == status, (path, status, response.status, str(result)[:500])
            return result, response.getheader("Set-Cookie", "").split(";")[0]
        finally:
            connection.close()

    def api(kind, role, data=None, status=200):
        return call("/api/logistica/" + kind, role, data, status)[0]

    def sale(quantity, customer="alto-verde"):
        return call("/api/comercio/pedidos", "06", {"action": "create", "customer": customer, "credit": False,
            "request_id": str(uuid4()), "lines": [{"sku": "VIL-CAN-15", "quantity": quantity}]})[0]

    try:
        cookies = {}
        for role, name in names.items():
            cookies[role] = call("/api/login", data={"username": name, "password": password})[1]
        assert b"El campo nos mueve" in call("/")[0]
        assert b"Iniciar" in call("/entrar")[0]
        call("/api/logistica/routes", status=401)
        for endpoint, allowed in {"picking": {"03", "04"}, "routes": {"07"}, "dispatch": {"03"},
                                  "deliveries": {"08"}, "tracking?id=no-existe": {"10"}}.items():
            for role in (f"{i:02}" for i in range(1, 11)):
                if role not in allowed:
                    api(endpoint, role, status=403)
        first, second, third = sale(15), sale(5), sale(1, "la-pradera")
        allocations = first["lines"][0]["reservations"]
        assert [(r["lot"], r["quantity"]) for r in allocations] == [("FEFO-PRIMERO", 10), ("L-VIL-CAN-15", 5)]
        api("tracking?id=" + first["id"], "otro", status=404)
        api("picking", "04", {"action": "scan", "id": first["id"], "sku": "VIL-CAN-15", "barcode": "2050000001024"}, 409)
        api("picking", "03", {"action": "finish", "id": first["id"]}, 409)
        for order in (first, second, third):
            api("picking", "04", {"action": "scan", "id": order["id"], "sku": "VIL-CAN-15", "barcode": "2050000001017"})
            # Repeated concurrent submissions cannot subtract the lot twice.
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: api("picking", "04", {"action": "finish", "id": order["id"]}), range(2)))
            assert all(row["status"] == "ALISTADO" for row in results)
        assert api("rotulo?id=" + first["id"], "03").startswith(b"%PDF-")
        setup = api("routes", "07")
        driver = next(row for row in setup["drivers"] if row["name"] == names["08"])
        api("routes", "07", {"action": "vehicle", "plate": "ABC123", "capacity": 299})
        api("routes", "07", {"action": "weight", "sku": "VIL-CAN-15", "kg": 15})
        api("routes", "07", {"action": "destination", "customer": "alto-verde", "address": "Finca Alto Verde",
                              "lat": 4.7, "lng": -74.1})
        api("routes", "07", {"action": "destination", "customer": "la-pradera", "address": "Finca La Pradera",
                              "lat": 4.8, "lng": -74.2})
        plan = {"action": "plan", "request_id": str(uuid4()), "vehicle": "ABC123", "driver": driver["id"],
                "departure": datetime.now(COLOMBIA).isoformat(timespec="minutes"), "lat": 4.6, "lng": -74.08,
                "orders": [first["id"], second["id"]]}
        assert "1 kg" in api("routes", "07", plan, 409)["error"]
        api("routes", "07", {"action": "vehicle", "plate": "ABC123", "capacity": 500})
        api("routes", "07", {**plan, "request_id": str(uuid4()), "orders": [first["id"], third["id"]]}, 400)
        route = api("routes", "07", plan)
        assert [stop["number"] for stop in route["stops"]] == sorted([first["number"], second["number"]])
        assert route["kg"] == 300 and len(route["stops"]) == 2
        assert api("routes", "07", plan)["id"] == route["id"]
        api("routes", "07", {**plan, "request_id": str(uuid4()), "orders": [third["id"]]}, 409)
        api("dispatch", "03", {"action": "dispatch", "id": route["id"]}, 409)
        api("dispatch", "03", {"action": "load", "id": route["id"], "label": third["number"]}, 409)
        for order in (first, second):
            api("dispatch", "03", {"action": "load", "id": route["id"], "label": order["number"]})
        dispatched = api("dispatch", "03", {"action": "dispatch", "id": route["id"]})
        assert dispatched["status"] == "EN_RUTA" and dispatched["manifest"].startswith("MD-")
        assert api("manifiesto?id=" + route["id"], "03").startswith(b"%PDF-")
        own = api("deliveries", "08")
        assert len(own["orders"]) == 2 and "lines" not in own["orders"][0]
        assert api("deliveries", "driver2")["orders"] == []
        api("evidence?id=" + first["id"], "driver2", status=404)
        tracked = api("tracking?id=" + first["id"], "10")
        assert tracked["eta"] and tracked["status"] == "EN_RUTA" and "stops" not in tracked
        api("tracking?id=" + first["id"], "otro", status=404)
        from PIL import Image
        image = BytesIO()
        Image.new("RGB", (120, 80), (23, 100, 57)).save(image, "PNG")
        proof = "data:image/png;base64," + base64.b64encode(image.getvalue()).decode()
        delivered = {"id": first["id"], "result": "ENTREGADO", "request_id": str(uuid4()),
                     "lat": 4.7, "lng": -74.1, "signature": proof, "photo": proof}
        api("deliveries", "driver2", delivered, 404)
        api("deliveries", "08", {**delivered, "signature": "not an image"}, 400)
        assert api("deliveries", "08", delivered)["status"] == "ENTREGADO"
        assert api("deliveries", "08", delivered)["saved"] is True
        novelty = {"id": second["id"], "result": "NOVEDAD", "note": "Cliente cerrado", "request_id": str(uuid4())}
        api("deliveries", "08", novelty)
        api("deliveries", "08", novelty)
        assert len(api("routes", "07")["alerts"]) == 1
        receive = {"action": "return", "id": second["id"], "location": "Retornos A1"}
        assert api("dispatch", "03", receive)["status"] == "RECIBIDO"
        assert api("dispatch", "03", receive)["status"] == "RECIBIDO"
        assert api("evidence?id=" + first["id"], "07")["photo"] == proof
        # Reopen the server and database, retain cookies and verify durable records.
        server.shutdown()
        server.server_close()
        worker.join()
        with app.database() as db:
            app.initialize_schema(db)
        server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        worker = start()
        assert api("tracking?id=" + first["id"], "10")["status"] == "ENTREGADO"
        assert api("evidence?id=" + first["id"], "07")["photo"] == proof
        assert api("deliveries", "08", delivered)["saved"]
        with app.database() as db:
            item = products(db)["VIL-CAN-15"]
            lots = list(app.run_db(db, "commerce_lots", "SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location", (item["id"],)))
            assert sum(lot["quantity"] for lot in lots) == 44
            assert sum(lot["reserved"] for lot in lots) == 0
        print("HU-11 a HU-15: FEFO, permisos, capacidad, PDF, pruebas de entrega, retornos, idempotencia y persistencia OK.")
        if os.environ.get("VILLALI_TEST_PREVIEW"):
            print("PREVIEW " + server.origin, flush=True)
            worker.join()
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporary:
        app.DB = Path(temporary) / "logistics.sqlite3"
        check()
