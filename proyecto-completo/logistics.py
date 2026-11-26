"""Picking, dispatch and delivery records stored with the existing transactional backend."""

import base64
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from math import asin, cos, radians, sin, sqrt
from uuid import uuid4

from app import Problem, audit, field, run_db, transaction
from commerce import COLOMBIA, all_records, find, number, products, require_record, save, sale_customer, update_lot

ACTIVE_ROUTES = {"PLANIFICADA", "EN_RUTA"}


def now():
    return datetime.now(COLOMBIA).isoformat(timespec="seconds")


def decimal_value(value, minimum, maximum):
    try:
        result = Decimal(str(value))
        if result.is_finite() and minimum <= result <= maximum:
            return float(result)
    except (InvalidOperation, ValueError, TypeError):
        pass
    raise Problem("Revisa el valor numérico indicado.")


def position(data):
    return {"lat": decimal_value(data.get("lat"), -90, 90),
            "lng": decimal_value(data.get("lng"), -180, 180)}


def drivers(db):
    return [dict(row) for row in run_db(db, "logistics_drivers",
            "SELECT id,name FROM users WHERE role='08' AND active=1")]


def distance(a, b):
    lat1, lat2 = radians(a["lat"]), radians(b["lat"])
    delta_lat = lat2 - lat1
    delta_lng = radians(b["lng"] - a["lng"])
    arc = sin(delta_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2)**2
    return 12742 * asin(sqrt(min(1, arc)))


def order_view(order):
    return {key: value for key, value in order.items() if key not in {"delivery", "credit"}}


def driver_order(order):
    return {"id": order["id"], "number": order["number"], "status": order["status"], "customer_name": order["customer_name"],
            "returnable": [{"sku": l["sku"], "name": l["name"], **r} for l in order["lines"] for r in l.get("reservations", [])]}


def find_route_order(db, order_id):
    return next((route for route in all_records(db, "rutas") if order_id in route["orders"]), None)


def confirm_pick(db, actor, data):
    order = require_record(db, "pedidos", data.get("id"))
    if order["status"] not in {"CONFIRMADO", "ALISTADO"}:
        raise Problem("Selecciona un pedido confirmado.", 409)
    if order["status"] == "ALISTADO":
        return order_view(order)
    catalog = products(db)
    sku = field(data, "sku")
    barcode = field(data, "barcode")
    item = catalog.get(sku)
    line = next((row for row in order["lines"] if row["sku"] == sku), None)
    if not item or not line or item["barcode"] != barcode:
        raise Problem("Producto incorrecto.", 409)
    line["picked"] = True
    line["picked_by"] = actor["id"]
    line["picked_at"] = now()
    save(db, "pedidos", order)
    return order_view(order)


def finish_pick(db, actor, data):
    order = require_record(db, "pedidos", data.get("id"))
    if order["status"] == "ALISTADO":
        return order_view(order)
    if order["status"] != "CONFIRMADO" or not all(line.get("picked") for line in order["lines"]):
        raise Problem("Confirma cada producto con su código antes de finalizar.", 409)
    catalog = products(db)
    for line in order["lines"]:
        item = catalog.get(line["sku"])
        if not item or not line.get("reservations") or sum(r["quantity"] for r in line["reservations"]) != line["quantity"]:
            raise Problem("El pedido necesita reservas completas. Revisa el inventario.", 409)
        lots = list(run_db(db, "commerce_lots", "SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location",
                           (item["id"],)))
        for reservation in line["reservations"]:
            lot = next((row for row in lots if row["lot"] == reservation["lot"] and row["location"] == reservation["location"]), None)
            count = reservation["quantity"]
            if not lot or lot["reserved"] < count or lot["quantity"] < count:
                raise Problem("El saldo reservado cambió. Revisa el lote antes de alistar.", 409)
            if lot["expiry"] < datetime.now(COLOMBIA).date().isoformat():
                raise Problem("El lote reservado está vencido. Solicita revisión de bodega.", 409)
            update_lot(db, lot, lot["quantity"] - count, lot["reserved"] - count)
    order.update(status="ALISTADO", picked_at=now(), picked_by=actor["id"])
    save(db, "pedidos", order)
    return order_view(order)


def save_vehicle(db, data):
    plate = field(data, "plate", 12).upper()
    row = {"id": plate, "plate": plate, "capacity": decimal_value(data.get("capacity"), 1, 100000),
           "active": True}
    if any(route["vehicle"] == plate and route["status"] in ACTIVE_ROUTES for route in all_records(db, "rutas")):
        raise Problem("El vehículo tiene una ruta pendiente. Finalízala antes de editar su capacidad.", 409)
    return save(db, "vehiculos", row)


def save_destination(db, data):
    customer = require_record(db, "clientes", data.get("customer"))
    return save(db, "destinos", {"id": customer["id"], **position(data),
                                "address": field(data, "address"), "zone": customer["zone"]})


def save_weight(db, data):
    sku = field(data, "sku")
    if sku not in products(db):
        raise Problem("Selecciona un producto activo.")
    return save(db, "pesos", {"id": sku, "kg": decimal_value(data.get("kg"), .001, 10000)})


def plan_route(db, actor, data):
    request_id = field(data, "request_id", 64)
    key = "RT-" + request_id
    existing = find(db, "rutas", key)
    if existing:
        return existing
    vehicle = require_record(db, "vehiculos", data.get("vehicle"))
    driver = next((row for row in drivers(db) if row["id"] == number(data.get("driver"))), None)
    if not vehicle["active"] or not driver:
        raise Problem("Selecciona un vehículo y un conductor activos.")
    chosen = data.get("orders")
    if not isinstance(chosen, list) or not 1 <= len(chosen) <= 30 or any(not isinstance(key, str) for key in chosen):
        raise Problem("Selecciona entre uno y treinta pedidos alistados.")
    if len(set(chosen)) != len(chosen):
        raise Problem("Selecciona cada pedido una sola vez.")
    routes = all_records(db, "rutas")
    busy = [route for route in routes if route["status"] in ACTIVE_ROUTES]
    if any(route["vehicle"] == vehicle["id"] or route["driver"] == driver["id"] for route in busy):
        raise Problem("El vehículo o conductor ya tiene una ruta pendiente.", 409)
    origin = position(data)
    route_date = field(data, "departure", 32)
    try:
        departure = datetime.fromisoformat(route_date)
        if departure.tzinfo is None:
            departure = departure.replace(tzinfo=COLOMBIA)
    except ValueError:
        raise Problem("Indica una fecha y hora de salida válidas.") from None
    if departure < datetime.now(COLOMBIA) - timedelta(minutes=15):
        raise Problem("La salida debe programarse desde la fecha actual.")
    destinations = {row["id"]: row for row in all_records(db, "destinos")}
    weights = {row["id"]: row["kg"] for row in all_records(db, "pesos")}
    stops = []
    zones = set()
    total_weight = Decimal(0)
    for order_id in chosen:
        order = require_record(db, "pedidos", order_id)
        if order["status"] != "ALISTADO" or find_route_order(db, order_id):
            raise Problem("Un pedido ya tiene ruta o aún no está alistado.", 409)
        customer = require_record(db, "clientes", order["customer"])
        destination = destinations.get(customer["id"])
        if not destination:
            raise Problem(f"Registra la dirección y coordenadas de {customer['name']}.")
        zones.add(customer["zone"].strip().casefold())
        weight = Decimal(0)
        for line in order["lines"]:
            if line["sku"] not in weights:
                raise Problem(f"Configura el peso por unidad de {line['sku']}.")
            weight += Decimal(str(weights[line["sku"]])) * line["quantity"]
        total_weight += weight
        stops.append({"order": order_id, "number": order["number"], "customer": customer["name"],
                      "destination": destination, "kg": float(weight)})
    if len(zones) != 1:
        raise Problem("Agrupa pedidos de la misma zona.")
    if total_weight > Decimal(str(vehicle["capacity"])):
        extra = total_weight - Decimal(str(vehicle["capacity"]))
        raise Problem(f"Excede la capacidad en {extra.normalize():f} kg.", 409)
    ordered, cursor, eta = [], origin, departure
    while stops:
        stop = min(stops, key=lambda row: (distance(cursor, row["destination"]), row["number"]))
        stops.remove(stop)
        km = distance(cursor, stop["destination"])
        eta += timedelta(minutes=max(5, km / 30 * 60))
        stop["eta"] = eta.isoformat(timespec="minutes")
        ordered.append(stop)
        cursor = stop["destination"]
        eta += timedelta(minutes=15)
    route = {"id": key, "number": "RT-" + uuid4().hex[:8].upper(), "status": "PLANIFICADA",
             "vehicle": vehicle["id"], "driver": driver["id"], "driver_name": driver["name"],
             "orders": [stop["order"] for stop in ordered], "stops": ordered, "origin": origin,
             "departure": departure.isoformat(timespec="minutes"), "kg": float(total_weight),
             "loaded": [], "created_by": actor["id"], "date": now()}
    return save(db, "rutas", route)


def load_order(db, data):
    route = require_record(db, "rutas", data.get("id"))
    if route["status"] != "PLANIFICADA":
        raise Problem("El cargue requiere una ruta planificada.", 409)
    label = field(data, "label")
    order = next((row for row in all_records(db, "pedidos") if row["number"] == label), None)
    if not order:
        raise Problem("Rótulo de pedido no encontrado.", 404)
    if order["id"] not in route["orders"]:
        other = find_route_order(db, order["id"])
        raise Problem(f"Pedido de otra ruta ({other['number'] if other else 'sin asignación'}).", 409)
    if order["status"] != "ALISTADO":
        raise Problem("El pedido ya cambió de estado.", 409)
    if order["id"] not in route["loaded"]:
        route["loaded"].append(order["id"])
        save(db, "rutas", route)
    return route


def dispatch_route(db, data):
    route = require_record(db, "rutas", data.get("id"))
    if route["status"] == "EN_RUTA":
        return route
    if route["status"] != "PLANIFICADA" or set(route["loaded"]) != set(route["orders"]):
        raise Problem("Escanea todos los rótulos de esta ruta antes de emitir el manifiesto.", 409)
    for key in route["orders"]:
        order = require_record(db, "pedidos", key)
        if order["status"] != "ALISTADO":
            raise Problem("Revisa el estado de los pedidos antes de despachar.", 409)
        save(db, "pedidos", {**order, "status": "EN_RUTA", "dispatched_at": now(), "route": route["id"]})
    route.update(status="EN_RUTA", dispatched_at=now(), manifest="MD-" + route["number"][3:])
    return save(db, "rutas", route)


def evidence(value):
    if not isinstance(value, str) or not value.startswith("data:image/png;base64,") and not value.startswith("data:image/jpeg;base64,"):
        raise Problem("Adjunta una imagen de firma y una fotografía válidas.")
    try:
        raw = base64.b64decode(value.split(",", 1)[1], validate=True)
        from PIL import Image
        with Image.open(BytesIO(raw)) as image:
            image.verify()
        if not 100 <= len(raw) <= 600000:
            raise ValueError
    except Exception:
        raise Problem("La imagen es inválida o supera 600 KB.") from None
    return value


def delivery(db, actor, data):
    order = require_record(db, "pedidos", data.get("id"))
    route = find_route_order(db, order["id"])
    if not route or route["driver"] != actor["id"]:
        raise Problem("Entrega no encontrada.", 404)
    key = field(data, "request_id", 64)
    if order.get("delivery", {}).get("id") == key:
        return {"id": order["id"], "status": order["status"], "saved": True}
    if order["status"] != "EN_RUTA" or route["status"] != "EN_RUTA":
        raise Problem("La entrega ya fue registrada o todavía no salió de bodega.", 409)
    result = data.get("result")
    if result not in {"ENTREGADO", "NOVEDAD"}:
        raise Problem("Selecciona el resultado de la entrega.")
    record = {"id": key, "by": actor["id"], "at": now(), "note": str(data.get("note", ""))[:600]}
    try:
        captured = datetime.fromisoformat(str(data.get("captured_at", record["at"])).replace("Z", "+00:00"))
        if captured.tzinfo is None or not datetime.now(COLOMBIA) - timedelta(days=7) <= captured <= datetime.now(COLOMBIA) + timedelta(minutes=5):
            raise ValueError
    except ValueError:
        raise Problem("Revisa la fecha de captura y sincroniza dentro de siete días.") from None
    record["captured_at"] = captured.isoformat(timespec="seconds")
    if result == "ENTREGADO":
        record.update(position(data))
        record.update(signature=evidence(data.get("signature")), photo=evidence(data.get("photo")))
        import json
        returned = data.get("returned_lines", [])
        if not isinstance(returned, list) or len(returned) > 200:
            raise Problem("Revisa los lotes devueltos.")
        return_lines, delivered_lines, seen = [], [], set()
        for selected in returned:
            if not isinstance(selected, dict):raise Problem("Lote devuelto inválido.")
            ident = (selected.get("sku"), selected.get("lot"), selected.get("location"))
            line = next((l for l in order["lines"] if l["sku"] == ident[0]), None)
            allocation = next((r for r in line.get("reservations", []) if (r["lot"],r["location"]) == ident[1:]), None) if line else None
            from commerce import number
            qty = number(selected.get("quantity"), 1)
            if not allocation or ident in seen or qty > allocation["quantity"]:raise Problem("La devolución supera el lote cargado.")
            seen.add(ident)
            return_lines.append({**line,"quantity":qty,"reservations":[{**allocation,"quantity":qty}]})
        for line in order["lines"]:
            qty = line["quantity"] - sum(l["quantity"] for l in return_lines if l["sku"] == line["sku"])
            if qty:delivered_lines.append({**json.loads(json.dumps(line)),"quantity":qty})
        if not delivered_lines:raise Problem("Si no se entregó ninguna unidad, registra No entregado / novedad.")
        order["delivered_lines"] = delivered_lines
        if return_lines:
            save(db,"retornos",{"id":order["id"],"order_id":order["id"],"order":order["number"],"route":route["number"],
                "status":"PENDIENTE_RECEPCION","lines":return_lines,"note":record["note"] or "Devolución parcial en entrega","at":now(),"excluded_from_invoice":True})
    else:
        record["note"] = field(data, "note", 600)
        save(db, "retornos", {"id": order["id"], "order_id": order["id"], "excluded_from_invoice": True, "order": order["number"], "route": route["number"],
                              "status": "PENDIENTE_RECEPCION", "lines": order["lines"], "note": record["note"], "at": now()})
        save(db, "avisos_logistica", {"id": key, "order": order["number"], "note": record["note"],
                                     "route": route["number"], "at": now()})
    order.update(status=result, delivery=record)
    save(db, "pedidos", order)
    statuses = [require_record(db, "pedidos", item)["status"] for item in route["orders"]]
    if all(status in {"ENTREGADO", "NOVEDAD", "CERRADO"} for status in statuses):
        save(db, "rutas", {**route, "status": "FINALIZADA", "finished_at": now()})
    return {"id": order["id"], "status": result, "saved": True}


def receive_return(db, data, actor=None):
    from finance import inspect_return
    return inspect_return(db, actor or {"id": 0}, {**data, "decision": "REINGRESO", "reason": "Inspección: retorno íntegro recibido en bodega"})


def tracking(db, actor, key):
    customer = sale_customer(db, actor)
    order = find(db, "pedidos", key)
    if not customer or not order or order["customer"] != customer["id"]:
        raise Problem("Pedido no encontrado.", 404)
    route = find_route_order(db, key)
    eta, ahead = None, None
    if route and order["status"] == "EN_RUTA":
        index = route["orders"].index(key)
        ahead = sum(require_record(db, "pedidos", item)["status"] == "EN_RUTA" for item in route["orders"][:index])
        stop = next(stop for stop in route["stops"] if stop["order"] == key)
        eta = max(datetime.fromisoformat(stop["eta"]), datetime.now(COLOMBIA) + timedelta(minutes=15 + 20 * ahead)).isoformat(timespec="minutes")
    timeline = [{"label": "Pendiente de revisión" if order["status"] == "PENDIENTE_REVISIÓN" else "Confirmado",
                 "at": order.get("confirmed_at", order["date"])}]
    for label, prop in (("Alistado", "picked_at"), ("En ruta", "dispatched_at")):
        if order.get(prop):
            timeline.append({"label": label, "at": order[prop]})
    if order.get("delivery"):
        timeline.append({"label": "Entregado" if order["status"] in {"ENTREGADO", "CERRADO"} else "Novedad", "at": order["delivery"].get("captured_at", order["delivery"]["at"])})
    for label, prop in (("Facturado", "invoiced_at"), ("Cerrado", "closed_at")):
        if order.get(prop):timeline.append({"label": label, "at": order[prop]})
    return {"number": order["number"], "status": order["status"], "timeline": timeline, "eta": eta, "ahead": ahead}


def pdf_document(db, kind, key):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from xml.sax.saxutils import escape
    import qrcode
    output = BytesIO()
    document = SimpleDocTemplate(output)
    style = getSampleStyleSheet()
    parts = [Paragraph("Distribuidora Villali", style["Title"]), Spacer(1, 14)]
    if kind == "rotulo":
        order = require_record(db, "pedidos", key)
        if order["status"] not in {"ALISTADO", "EN_RUTA", "ENTREGADO", "CERRADO", "NOVEDAD"}:
            raise Problem("Finaliza el alistamiento antes de generar el rótulo.", 409)
        parts += [Paragraph(escape(order["number"]), style["Heading1"]),
                  Paragraph(escape(order["customer_name"]), style["Normal"])]
        qr = BytesIO()
        qrcode.make(order["number"]).save(qr, format="PNG")
        qr.seek(0)
        parts.append(Image(qr, width=150, height=150))
        name = order["number"] + ".pdf"
    else:
        route = require_record(db, "rutas", key)
        if not route.get("manifest"):
            raise Problem("Despacha la ruta para emitir su manifiesto.", 409)
        parts += [Paragraph(escape(route["manifest"]), style["Heading1"]),
                  Paragraph(escape(f"{route['number']} · {route['vehicle']} · {route['driver_name']}"), style["Normal"]),
                  Paragraph(escape(f"{route['kg']} kg · {route['dispatched_at']}"), style["Normal"]), Spacer(1, 12)]
        rows = [[Paragraph(h, style["Normal"]) for h in ("Visita", "Pedido", "Cliente / dirección")]]
        for index, stop in enumerate(route["stops"], 1):
            rows.append([str(index), Paragraph(escape(stop["number"]), style["Normal"]),
                         Paragraph(escape(stop["customer"] + " · " + stop["destination"]["address"]), style["Normal"])])
        table = Table(rows, colWidths=[40, 150, 290], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce9dd")),
                                   ("GRID", (0, 0), (-1, -1), .4, colors.lightgrey),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
        parts.append(table)
        name = route["manifest"] + ".pdf"
    document.build(parts)
    return output.getvalue(), name


def dispatch(handler, db, actor, method, kind, query):
    roles = {"picking": {"03", "04"}, "routes": {"07"}, "dispatch": {"03"}, "deliveries": {"08"},
             "tracking": {"10"}, "rotulo": {"03", "04", "07"}, "manifiesto": {"03", "07"},
             "evidence": {"03", "07", "08"}}
    handler.require(db, actor, roles.get(kind, set()), "/api/logistica/" + kind)
    if method == "GET":
        if kind in {"rotulo", "manifiesto"}:
            content, name = pdf_document(db, kind, query.get("id", [""])[0])
            return handler.respond(content, content_type="application/pdf", Content_Disposition=f'inline; filename="{name}"')
        if kind == "tracking":
            return handler.respond(tracking(db, actor, query.get("id", [""])[0]))
        if kind == "evidence":
            order = require_record(db, "pedidos", query.get("id", [""])[0])
            route = find_route_order(db, order["id"])
            if actor["role"] == "08" and (not route or route["driver"] != actor["id"]):
                raise Problem("Entrega no encontrada.", 404)
            return handler.respond(order.get("delivery", {}))
        orders = all_records(db, "pedidos")
        routes = all_records(db, "rutas")
        if kind == "picking":
            return handler.respond({"orders": [order_view(row) for row in orders if row["status"] in {"CONFIRMADO", "ALISTADO"}]})
        if kind == "routes":
            assigned = {key for route in routes for key in route["orders"]}
            customers = all_records(db, "clientes")
            return handler.respond({"orders": [order_view(row) for row in orders if row["status"] == "ALISTADO" and row["id"] not in assigned],
                                    "routes": routes, "vehicles": all_records(db, "vehiculos"), "drivers": drivers(db),
                                    "customers": [{"id": row["id"], "name": row["name"], "zone": row["zone"]} for row in customers],
                                    "destinations": all_records(db, "destinos"), "products": list(products(db).values()),
                                    "weights": all_records(db, "pesos"), "alerts": all_records(db, "avisos_logistica")[-30:],
                                    "returns": all_records(db, "retornos")})
        if kind == "dispatch":
            return handler.respond({"routes": [row for row in routes if row["status"] in ACTIVE_ROUTES],
                                    "returns": all_records(db, "retornos")})
        mine = [row for row in routes if row["driver"] == actor["id"] and
                (row["status"] in ACTIVE_ROUTES or row.get("finished_at", "")[:10] == datetime.now(COLOMBIA).date().isoformat())]
        selected = {key for route in mine for key in route["orders"]}
        return handler.respond({"routes": mine, "orders": [driver_order(row) for row in orders if row["id"] in selected]})
    if method != "POST":
        raise Problem("Método no permitido.", 405)
    data = handler.data(1_800_000 if kind == "deliveries" else 32768)
    with transaction(db):
        current = run_db(db, "user_by_id", "SELECT * FROM users WHERE id=?", (actor["id"],)).fetchone()
        if not current or not current["active"] or current["role"] != actor["role"]:
            raise Problem("Inicia sesión de nuevo.", 401)
        action = data.get("action")
        if kind == "picking":
            if action == "scan":
                result = confirm_pick(db, actor, data)
            elif action == "finish":
                result = finish_pick(db, actor, data)
            else:
                raise Problem("Selecciona una acción de alistamiento.")
        elif kind == "routes":
            operations = {"vehicle": lambda: save_vehicle(db, data),
                          "destination": lambda: save_destination(db, data),
                          "weight": lambda: save_weight(db, data),
                          "plan": lambda: plan_route(db, actor, data)}
            if action not in operations:
                raise Problem("Selecciona una acción de planificación.")
            result = operations[action]()
        elif kind == "dispatch":
            if action == "load":
                result = load_order(db, data)
            elif action == "dispatch":
                result = dispatch_route(db, data)
            elif action == "return":
                result = receive_return(db, data, actor)
            else:
                raise Problem("Selecciona una acción de despacho.")
        elif kind == "deliveries":
            result = delivery(db, actor, data)
        else:
            raise Problem("Método no permitido.", 405)
        audit(db, actor["username"], "LOGISTICA_" + kind.upper(), handler.ip, str(data.get("id", result.get("id", ""))))
    return handler.respond(result)
