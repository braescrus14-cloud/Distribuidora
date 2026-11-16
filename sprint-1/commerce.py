import calendar
import json
import re
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from app import Problem, audit, field, run_db, send_email, transaction

ROLES = {"proveedores": {"05"}, "compras": {"01", "03", "04", "05"},
         "clientes": {"01", "06"}, "pedidos": {"06", "10"}}
PURCHASE_LIMIT = 1_000_000_000
COLOMBIA = timezone(timedelta(hours=-5))
NIT_WEIGHTS = (3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71)


def all_records(db, kind):
    rows = run_db(db, "commerce_list", "SELECT payload FROM commerce_records WHERE kind=?", (kind,))
    return sorted((json.loads(row["payload"]) for row in rows), key=lambda row: row.get("name", row["id"]))


def find(db, kind, key):
    if not isinstance(key, str):
        return None
    row = run_db(db, "commerce_get", "SELECT payload FROM commerce_records WHERE kind=? AND record_key=?",
                 (kind, key)).fetchone()
    return json.loads(row["payload"]) if row else None


def require_record(db, kind, key):
    row = find(db, kind, key)
    if not row:
        raise Problem("Registro no encontrado.", 404)
    return row


def save(db, kind, row):
    run_db(db, "commerce_save", """INSERT INTO commerce_records VALUES(?,?,?)
        ON CONFLICT(kind,record_key) DO UPDATE SET payload=excluded.payload""",
        (kind, row["id"], json.dumps(row, ensure_ascii=False)))
    return row


def number(value, minimum=0):
    if re.fullmatch(r"[0-9]{1,12}", str(value)) and int(value) >= minimum:
        return int(value)
    raise Problem("Indica una cantidad o valor válido.")


def nit_digit(nit):
    remainder = sum(int(digit) * weight for digit, weight in zip(reversed(nit), NIT_WEIGHTS)) % 11
    return remainder if remainder < 2 else 11 - remainder


def products(db):
    fields = ("id", "sku", "name", "barcode", "price_cents", "species")
    rows = run_db(db, "commerce_products", """SELECT id,sku,name,barcode,price_cents,species
        FROM products WHERE active=1 ORDER BY name""")
    return {row["sku"]: {key: row[key] for key in fields} for row in rows}


def accounts(db):
    return [{"id": row["id"], "name": row["name"], "role": row["role"]} for row in run_db(
        db, "commerce_accounts", "SELECT id,name,role FROM users WHERE active=1 AND role IN ('06','10')")]


def product_lots(db, product):
    return list(run_db(db, "commerce_lots", """SELECT * FROM lots WHERE product_id=?
        ORDER BY expiry,lot,location""", (product["id"],)))


def available_lots(db, product, today):
    return [row for row in product_lots(db, product)
            if row["expiry"] >= today.isoformat() and row["quantity"] > row["reserved"]
            and not row["lot"].startswith("DEMO-IT-")]


def stock_overview(db, today):
    rows = run_db(db, "commerce_stock", """SELECT product_id, SUM(quantity - reserved) AS available FROM lots
        WHERE expiry>=? AND substr(lot,1,8)<>'DEMO-IT-' GROUP BY product_id""", (today.isoformat(),))
    return {row["product_id"]: row["available"] for row in rows}


def update_lot(db, lot, quantity, reserved):
    run_db(db, "commerce_lot_update", """UPDATE lots SET quantity=?,reserved=?
           WHERE product_id=? AND lot=? AND location=?""",
           (quantity, reserved, lot["product_id"], lot["lot"], lot["location"]))


def provider(db, data):
    nit = field(data, "nit", 17)
    if not re.fullmatch(r"[0-9]{1,15}-[0-9]", nit) or nit_digit(nit[:-2]) != int(nit[-1]):
        raise Problem("NIT inválido.")
    original = find(db, "proveedores", nit)
    if original and data.get("id") != nit:
        raise Problem("Ya existe un proveedor con ese NIT.", 409)
    if data.get("id") and data["id"] != nit:
        raise Problem("El NIT registrado es fijo.")
    skus = data.get("skus")
    catalog = products(db)
    if not isinstance(skus, list) or not skus or any(not isinstance(sku, str) or sku not in catalog for sku in skus):
        raise Problem("Asocia al menos un producto activo.")
    return save(db, "proveedores", {"id": nit, "name": field(data, "name"), "contact": field(data, "contact"),
                                   "terms": field(data, "terms"), "active": data.get("active") is True,
                                   "skus": sorted(set(skus))})


def client(db, actor, data):
    if actor["role"] == "01":
        row = require_record(db, "clientes", data.get("id"))
        row["credit"] = number(data.get("credit"))
        row["balance"] = number(data.get("balance"))
        due = data.get("due") or ""
        if row["balance"] and not due:
            raise Problem("Indica el vencimiento de la cartera pendiente.")
        if due:
            read_date(due)
        row["due"] = due
        return save(db, "clientes", row)
    if any(key in data for key in ("credit", "balance", "due")):
        raise Problem("Solo el Gerente General puede modificar cupos y cartera.", 403)
    original = require_record(db, "clientes", data["id"]) if data.get("id") else None
    if data.get("consent") is not True:
        raise Problem("Registra la autorización de datos.")
    kind = data.get("type")
    if kind not in ("mayorista", "minorista"):
        raise Problem("Selecciona el tipo de cliente.")
    account = number(data.get("account", 0))
    if account:
        if not any(row["id"] == account and row["role"] == "10" for row in accounts(db)):
            raise Problem("Selecciona una cuenta de cliente activa.")
        if any(row["account"] == account and row["id"] != data.get("id") for row in all_records(db, "clientes")):
            raise Problem("La cuenta ya está vinculada a otro cliente.", 409)
    if original and original["advisor"] not in (0, actor["id"]):
        raise Problem("Acceso denegado.", 403)
    row = original or {"id": uuid4().hex, "advisor": actor["id"], "credit": 0, "balance": 0, "due": ""}
    row.update(name=field(data, "name"), zone=field(data, "zone"), type=kind, account=account,
               advisor=actor["id"], consent=True, active=data.get("active") is True,
               price_list="A" if kind == "mayorista" else "B")
    return save(db, "clientes", row)


def unlink_portal_account(db, user_id):
    for row in all_records(db, "clientes"):
        if row["account"] == user_id:
            save(db, "clientes", {**row, "account": 0})


def read_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise Problem("Indica una fecha válida.") from None


def six_months(today):
    year, month = divmod(today.month + 5, 12)
    return date(today.year + year, month + 1, min(today.day, calendar.monthrange(today.year + year, month + 1)[1]))


def line_items(data, catalog, price_for):
    lines = data.get("lines")
    if not isinstance(lines, list) or not 1 <= len(lines) <= 50:
        raise Problem("Agrega entre 1 y 50 productos.")
    result = []
    seen = set()
    for line in lines:
        sku = line.get("sku") if isinstance(line, dict) else None
        if not isinstance(sku, str) or sku not in catalog or sku in seen:
            raise Problem("Selecciona productos activos y evita repetirlos.")
        seen.add(sku)
        item = catalog[sku]
        quantity = number(line.get("quantity"), 1)
        if quantity > 1_000_000:
            raise Problem("La cantidad por línea supera el máximo.")
        result.append({"sku": sku, "name": item["name"], "quantity": quantity,
                       "price": price_for(item, line)})
    return result


def total(lines):
    return sum(line["price"] * line["quantity"] for line in lines)


def new_order(data, kind, db, actor):
    request_id = data.get("request_id")
    if not isinstance(request_id, str) or not re.fullmatch(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}", request_id):
        raise Problem("Identificador de solicitud inválido.")
    key = request_id.replace("-", "")
    existing = find(db, kind, key)
    if existing and existing["created_by"] != actor["id"]:
        raise Problem("Acceso denegado.", 403)
    return existing, {"id": key, "number": f"{'OC' if kind == 'compras' else 'PV'}-{key[:12].upper()}",
                      "created_by": actor["id"], "date": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def purchase(db, actor, data, today):
    action = data.get("action")
    if action == "create" and actor["role"] == "05":
        existing, order = new_order(data, "compras", db, actor)
        if existing:
            return existing
        vendor = require_record(db, "proveedores", data.get("supplier"))
        if not vendor["active"]:
            raise Problem("Selecciona un proveedor activo.")
        catalog = {sku: product for sku, product in products(db).items() if sku in vendor["skus"]}
        lines = line_items(data, catalog, lambda item, line: number(line.get("cost"), 1) * 100)
        for line in lines:
            line["received"] = 0
        amount = total(lines)
        order.update(supplier=vendor["id"], supplier_name=vendor["name"], lines=lines, total=amount,
                     status="Pendiente de aprobación" if amount > PURCHASE_LIMIT else "Aprobada", receipts=[])
        return save(db, "compras", order)
    if action == "approve" and actor["role"] == "01":
        order = require_record(db, "compras", data.get("id"))
        if order["status"] != "Pendiente de aprobación":
            raise Problem("La orden ya fue procesada.", 409)
        order["status"] = "Aprobada"
        order["approved_by"] = actor["id"]
        return save(db, "compras", order)
    if action == "receive" and actor["role"] in {"03", "04"}:
        order = require_record(db, "compras", data.get("id"))
        receipt_key = field(data, "request_id", 36)
        if any(row["id"] == receipt_key for row in order["receipts"]):
            return order
        if order["status"] not in {"Aprobada", "Recibida parcial"}:
            raise Problem("La orden debe estar aprobada y tener unidades pendientes.", 409)
        code = field(data, "sku").upper()
        catalog = products(db)
        product = catalog.get(code) or next((row for row in catalog.values() if row["barcode"] == code), None)
        line = next((row for row in order["lines"] if product and row["sku"] == product["sku"]), None)
        quantity = number(data.get("quantity"), 1)
        if not line:
            raise Problem("El código no corresponde a un producto de esta orden.")
        pending = line["quantity"] - line["received"]
        if quantity > pending:
            raise Problem(f"Solo quedan {pending} unidades pendientes de este producto.")
        expiry = read_date(data.get("expiry"))
        if expiry < six_months(today):
            raise Problem("Vida útil insuficiente. El vencimiento debe quedar al menos a seis meses.")
        lot, location = field(data, "lot").upper(), field(data, "location")
        if lot.startswith("DEMO-IT-"):
            raise Problem("Indica un código de lote de recepción.")
        matching_lots = [row for row in product_lots(db, product) if row["lot"].upper() == lot]
        if any(row["expiry"] != expiry.isoformat() for row in matching_lots):
            raise Problem("Ese lote ya está registrado con otro vencimiento.", 409)
        previous = next((row for row in matching_lots if row["location"] == location), None)
        if any(other["supplier"] != order["supplier"] and
               any(r["sku"] == line["sku"] and r["lot"].upper() == lot for r in other["receipts"])
               for other in all_records(db, "compras")):
            raise Problem("Este lote ya se recibió de otro proveedor.", 409)
        receipt = {"id": receipt_key, "sku": line["sku"], "lot": lot, "location": location,
                   "expiry": expiry.isoformat(), "quantity": quantity, "date": today.isoformat(), "by": actor["id"]}
        if previous:
            if previous["quantity"] + quantity > 2_000_000_000:
                raise Problem("El saldo supera el máximo permitido.")
            update_lot(db, previous, previous["quantity"] + quantity, previous["reserved"])
        else:
            run_db(db, "commerce_lot_add", """INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved)
                VALUES(?,?,?,?,?,?)""", (product["id"], lot, receipt["expiry"], location, quantity, 0))
        order["receipts"].append(receipt)
        line["received"] += quantity
        order["status"] = ("Recibida completa" if all(row["received"] == row["quantity"] for row in order["lines"])
                           else "Recibida parcial")
        return save(db, "compras", order)
    raise Problem("Acceso denegado.", 403)


def price(item, customer):
    return (item["price_cents"] * 95 + 50) // 100 if customer["price_list"] == "A" else item["price_cents"]


def sale_customer(db, actor, key=None):
    if actor["role"] == "10":
        matches = [row for row in all_records(db, "clientes") if row["account"] == actor["id"]]
        return matches[0] if len(matches) == 1 and matches[0]["active"] else None
    row = require_record(db, "clientes", key)
    if not row["active"] or row["advisor"] != actor["id"]:
        raise Problem("El cliente debe estar activo y asignado a tu cuenta.", 403)
    return row


def sale(db, actor, data, today):
    catalog = products(db)
    if data.get("action") == "confirm" and actor["role"] == "06":
        order = require_record(db, "pedidos", data.get("id"))
        customer = sale_customer(db, actor, order["customer"])
        if order["status"] == "CONFIRMADO":
            return order
        lines = line_items({"lines": order["lines"]}, catalog, lambda item, line: price(item, customer))
        credit = order["credit"]
    elif data.get("action") == "create":
        if actor["role"] == "10" and "customer" in data:
            raise Problem("El pedido se registra para la ficha vinculada a tu cuenta.", 403)
        customer = sale_customer(db, actor, data.get("customer"))
        if not customer:
            raise Problem("Pide al asesor que vincule tu cuenta con una única ficha activa.", 403)
        existing, order = new_order(data, "pedidos", db, actor)
        if existing:
            if existing["customer"] != customer["id"]:
                raise Problem("Acceso denegado.", 403)
            return existing
        lines = line_items(data, catalog, lambda item, line: price(item, customer))
        credit = data.get("credit") is True
    else:
        raise Problem("Acceso denegado.", 403)
    amount = total(lines)
    if actor["role"] == "06" and credit:
        if customer["balance"] and customer["due"] and read_date(customer["due"]) < today:
            raise Problem("Cliente con cartera vencida.", 409)
        committed = sum(row["total"] for row in all_records(db, "pedidos")
                        if row["customer"] == customer["id"] and row["credit"] and row["status"] == "CONFIRMADO")
        if amount + customer["balance"] + committed > customer["credit"]:
            raise Problem("Cupo de crédito insuficiente.", 409)
    for line in lines:
        lots = available_lots(db, catalog[line["sku"]], today)
        available = sum(row["quantity"] - row["reserved"] for row in lots)
        pending = line["quantity"]
        if pending > available:
            raise Problem(f"{line['sku']} · Disponible: {available}", 409)
        if actor["role"] == "10":
            continue
        line["reservations"] = []
        for lot in lots:
            count = min(pending, lot["quantity"] - lot["reserved"])
            update_lot(db, lot, lot["quantity"], lot["reserved"] + count)
            line["reservations"].append({"lot": lot["lot"], "location": lot["location"], "quantity": count})
            pending -= count
            if not pending:
                break
    order.update(customer=customer["id"], customer_name=customer["name"], advisor=customer["advisor"],
                 credit=credit, lines=lines, total=amount,
                 status="PENDIENTE_REVISIÓN" if actor["role"] == "10" else "CONFIRMADO")
    return save(db, "pedidos", order)


def portal_order(order):
    return {**{key: order[key] for key in ("number", "status", "total", "date")},
            "lines": [{key: line[key] for key in ("name", "quantity", "price")} for line in order["lines"]]}


def dispatch(handler, db, actor, method, kind):
    handler.require(db, actor, ROLES.get(kind, set()), f"/api/comercio/{kind}")
    today = datetime.now(COLOMBIA).date()
    if method == "GET":
        rows = all_records(db, kind)
        data = {"rows": rows}
        if kind == "proveedores":
            data["products"] = list(products(db).values())
        elif kind == "compras" and actor["role"] == "05":
            data["products"] = list(products(db).values())
            data["suppliers"] = [row for row in all_records(db, "proveedores") if row["active"]]
        elif kind == "compras" and actor["role"] in {"03", "04"}:
            catalog = products(db)
            data["barcodes"] = {line["sku"]: catalog[line["sku"]]["barcode"] for order in rows
                                if order["status"] in {"Aprobada", "Recibida parcial"}
                                for line in order["lines"] if line["sku"] in catalog and line["received"] < line["quantity"]}
        elif kind == "clientes" and actor["role"] == "06":
            data["rows"] = [row for row in rows if row["advisor"] in (0, actor["id"])]
            taken = {row["account"]: row["id"] for row in rows if row["account"]}
            visible = {row["id"] for row in data["rows"]}
            data["accounts"] = [{**row, "linked": taken.get(row["id"])} for row in accounts(db)
                                if row["role"] == "10" and (row["id"] not in taken or taken[row["id"]] in visible)]
        elif kind == "pedidos":
            portal = actor["role"] == "10"
            customer = sale_customer(db, actor) if portal else None
            if portal:
                if not customer:
                    return handler.respond({"rows": [], "products": [], "portal": None})
                data["portal"] = {"name": customer["name"], "price_list": customer["price_list"]}
                data["rows"] = [portal_order(row) for row in rows if row["customer"] == customer["id"]]
            else:
                customers = [row for row in all_records(db, "clientes") if row["advisor"] == actor["id"]]
                allowed = {row["id"] for row in customers}
                data["rows"] = [row for row in rows if row["customer"] in allowed]
                data["customers"] = [{"id": row["id"], "name": row["name"], "price_list": row["price_list"]}
                                     for row in customers if row["active"]]
            stock = stock_overview(db, today)
            data["products"] = [{**product, "available": stock.get(product["id"], 0),
                                 "price_cents": price(product, customer) if portal else product["price_cents"]}
                                for product in products(db).values()]
        return handler.respond(data)
    data = handler.data()
    first_create = False
    with transaction(db):
        if kind in {"compras", "pedidos"} and data.get("action") == "create":
            request_id = data.get("request_id")
            first_create = isinstance(request_id, str) and not find(db, kind, request_id.replace("-", ""))
        if kind == "proveedores":
            result = provider(db, data)
        elif kind == "clientes":
            result = client(db, actor, data)
        elif kind == "compras":
            result = purchase(db, actor, data, today)
        else:
            result = sale(db, actor, data, today)
        audit(db, actor["username"], f"CAMBIO_{kind.upper()}", handler.ip, result["id"])
    if first_create and result.get("status") in {"Pendiente de aprobación", "PENDIENTE_REVISIÓN"}:
        recipients = run_db(db, "commerce_recipients", """SELECT user_contacts.email FROM users
            JOIN user_contacts ON users.id=user_contacts.user_id
            WHERE users.active=1 AND users.role=? AND (?=0 OR users.id=?)""",
            ("01", 0, 0) if kind == "compras" else ("06", result["advisor"], result["advisor"]))
        for index, recipient in enumerate(recipients):
            status = send_email(recipient["email"], "Villali · " + result["number"],
                                result["number"] + " · " + result["status"], f"{kind}-{result['id']}-{index}")
            audit(db, actor["username"], "AVISO_COMERCIAL", handler.ip, status)
    return handler.respond(portal_order(result) if kind == "pedidos" and actor["role"] == "10" else result)
