"""Sprint 4. Academic providers, durable accounting and stock reconciliation."""
import calendar
import hashlib
import hmac
import json
import secrets
import time
from datetime import date, datetime, timedelta
from io import BytesIO
from uuid import uuid4
from xml.etree.ElementTree import Element, SubElement, tostring

from app import Problem, audit, field, run_db, transaction
from commerce import COLOMBIA, all_records, find, nit_digit, number, products, read_date, require_record, sale_customer, save, update_lot

ACADEMIC = "Simulación académica: sin validez fiscal y sin movimientos de dinero real."
ROLES = {"facturas": {"09", "01", "10"}, "pagos": {"09", "10"}, "cartera": {"09", "01"},
         "liquidaciones": {"07"}, "devoluciones": {"03"}, "indicadores": {"01"}, "documento": {"09", "01", "10"},
         "pse": {"09", "10"}, "bandeja": {"09"}, "nota-credito": {"03", "09", "01", "10"}, "acta-ruta": {"07"}, "cortes": {"01"}}


def now():
    return datetime.now(COLOMBIA).isoformat(timespec="seconds")


def sequence(db, kind, prefix):
    row = find(db, "finance_counters", kind) or {"id": kind, "value": 0}
    row["value"] += 1
    save(db, "finance_counters", row)
    return f"{prefix}-DEMO-{row['value']:06}"


def money(value):
    return "$" + f"{value / 100:,.2f}"


def invoice_for(db, order):
    return find(db, "facturas", order)


def invoice_balance(db, invoice, totals=None):
    if totals is None:
        credits = sum(r["total"] for r in all_records(db, "notas_credito") if r["invoice"] == invoice["id"])
        paid = sum(r["amount"] for r in all_records(db, "pagos") if r["invoice"] == invoice["id"])
    else:
        credits, paid = totals.get(invoice["id"], [0, 0])
    net = invoice["total"] - credits
    return {**invoice, "credits": credits, "paid": paid, "net": net, "balance": max(0, net - paid),
            "customer_credit": max(0, paid - net)}


def invoice_rows(db):
    totals = {}
    for kind, amount, index in (("notas_credito", "total", 0), ("pagos", "amount", 1)):
        for row in all_records(db, kind):
            totals.setdefault(row["invoice"], [0, 0])[index] += row[amount]
    return [invoice_balance(db, row, totals) for row in all_records(db, "facturas")]


def refresh(db, invoice):
    row = invoice_balance(db, invoice)
    if row["status"] != "RECHAZADA":
        row["status"] = "PAGADA" if row["balance"] == 0 else "PAGO_PARCIAL" if row["paid"] else "EMITIDA"
    save(db, "facturas", row)
    order = require_record(db, "pedidos", row["order"])
    pending = any(r.get("order_id", r["id"]) == order["id"] and r["status"] == "PENDIENTE_RECEPCION" for r in all_records(db, "retornos"))
    if row["status"] == "PAGADA" and not pending:
        order.update(status="CERRADO", closed_at=order.get("closed_at", now()))
    elif order["status"] == "CERRADO":
        order.update(status="ENTREGADO")
        order.pop("closed_at", None)
    save(db, "pedidos", order)
    customer = require_record(db, "clientes", row["customer"])
    if "finance_opening_balance" not in customer:
        customer["finance_opening_balance"] = customer["balance"]
        customer["finance_opening_due"] = customer.get("due", "")
    outstanding = [r for r in invoice_rows(db) if r["customer"] == customer["id"] and r["status"] != "RECHAZADA"]
    customer["balance"] = customer["finance_opening_balance"] + sum(r["balance"] for r in outstanding)
    due = [r["due"] for r in outstanding if r["balance"]] + ([customer["finance_opening_due"]] if customer["finance_opening_balance"] and customer["finance_opening_due"] else [])
    customer["due"] = min(due, default="")
    save(db, "clientes", customer)
    return row


def emit_invoice(db, actor, data):
    order = require_record(db, "pedidos", data.get("order"))
    existing = invoice_for(db, order["id"])
    if existing and existing["status"] != "RECHAZADA":
        return invoice_balance(db, existing)
    if order["status"] not in {"ENTREGADO", "CERRADO"}:
        raise Problem("Solo se factura un pedido entregado.", 409)
    customer = require_record(db, "clientes", order["customer"])
    fiscal = {"nit": field(data, "nit", 17), "email": field(data, "email", 200), "name": customer["name"]}
    import re
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", fiscal["email"]):
        raise Problem("Indica el correo del destinatario de la simulación.")
    due = read_date(field(data, "due", 10)).isoformat()
    lines = order.get("delivered_lines", order["lines"])
    lines = [{key: line[key] for key in ("sku", "name", "quantity", "price")} for line in lines if line["quantity"] > 0]
    post_returns = [r for r in all_records(db, "retornos") if return_order_id(r) == order["id"] and r.get("post_delivery")]
    if any(r["status"] == "PENDIENTE_RECEPCION" for r in post_returns):
        raise Problem("Inspecciona las devoluciones posteriores a la entrega antes de emitir.", 409)
    for line in lines:
        line["quantity"] -= sum(l["quantity"] for r in post_returns for l in r["lines"] if l["sku"] == line["sku"])
    lines = [r for r in lines if r["quantity"] > 0]
    if not lines:
        raise Problem("El pedido no tiene cantidades entregadas para facturar.", 409)
    invoice = existing or {"id": order["id"], "number": sequence(db, "invoice", "FE"), "order": order["id"],
                          "order_number": order["number"], "customer": customer["id"], "issued_at": now(), "zone": customer["zone"]}
    invoice.update(lines=lines, total=sum(r["quantity"] * r["price"] for r in lines), fiscal=fiscal, due=due, academic=True,
                   status="RECHAZADA", reason="NIT del cliente inválido.", submitted_at=now(), issued_by=actor["id"])
    nit = fiscal["nit"]
    if re.fullmatch(r"[0-9]{1,15}-[0-9]", nit) and nit_digit(nit[:-2]) == int(nit[-1]):
        invoice.update(status="EMITIDA", reason="", cufe="DEMO-" + hashlib.sha384((invoice["number"] + nit + str(invoice["total"])).encode()).hexdigest())
    save(db, "facturas", invoice)
    if invoice["status"] == "EMITIDA":
        for returned in post_returns:
            save(db, "retornos", {**returned, "excluded_from_invoice": True})
        save(db, "fiscal_customers", {"id": customer["id"], **fiscal})
        order["invoiced_at"] = now()
        save(db, "pedidos", order)
        save(db, "bandeja_facturas", {"id": invoice["id"], "invoice": invoice["id"], "recipient": fiscal["email"],
             "status": "ENVIO_SIMULADO", "at": now(), "attachments": [invoice["number"] + ".pdf", invoice["number"] + ".xml"], "academic": True})
        return refresh(db, invoice)
    return invoice


def payment(db, actor, data, source="manual"):
    key = field(data, "request_id", 80)
    target = field(data, "invoice", 120)
    if target.startswith("opening-"):
        if source != "manual" or dict(actor).get("role") != "09":raise Problem("Solo Contabilidad registra abonos de saldos anteriores.",403)
        customer=require_record(db,"clientes",target[len("opening-"):]);amount=number(data.get("amount"),1);method=data.get("method")
        if method not in {"EFECTIVO","TRANSFERENCIA"}:raise Problem("Usa efectivo o transferencia para el saldo anterior.")
        previous=find(db,"pagos",key)
        if previous:
            if previous["invoice"]!=target or previous["amount"]!=amount or previous["method"]!=method:raise Problem("La solicitud ya se utilizó con otros datos.",409)
            return previous
        opening=customer.get("finance_opening_balance",customer["balance"])
        if amount>opening:raise Problem("El pago supera el saldo ("+money(opening)+").",409)
        customer.update(finance_opening_balance=opening-amount,finance_opening_due=customer.get("finance_opening_due",customer.get("due","")),balance=customer["balance"]-amount)
        due=[r["due"] for r in all_records(db,"facturas") if r["customer"]==customer["id"] and r["status"]!="RECHAZADA" and invoice_balance(db,r)["balance"]]
        if customer["finance_opening_balance"] and customer["finance_opening_due"]:due.append(customer["finance_opening_due"])
        customer["due"]=min(due,default="");save(db,"clientes",customer)
        return save(db,"pagos",{"id":key,"number":sequence(db,"payment","RC"),"invoice":target,"customer":customer["id"],"amount":amount,"method":method,"reference":field(data,"reference",150),"at":now(),"by":actor["id"],"source":source,"academic":True})
    invoice = require_record(db, "facturas", data.get("invoice"))
    amount = number(data.get("amount"), 1)
    if amount > 1_000_000_000_000:
        raise Problem("El valor supera el máximo permitido.")
    method = data.get("method")
    if method not in {"EFECTIVO", "TRANSFERENCIA", "PSE"} or method == "PSE" and source != "webhook":
        raise Problem("PSE solo se registra al confirmar el webhook firmado.")
    previous = find(db, "pagos", key)
    if previous:
        if previous["invoice"] != invoice["id"] or previous["amount"] != amount or previous["method"] != method:
            raise Problem("La solicitud ya se utilizó con otros datos.", 409)
        return previous
    row = invoice_balance(db, invoice)
    if invoice["status"] == "RECHAZADA":
        raise Problem("Reenvía y acepta la factura antes de registrar pagos.", 409)
    if amount > row["balance"]:
        raise Problem("El pago supera el saldo (" + money(row["balance"]) + ").", 409)
    paid = save(db, "pagos", {"id": key, "number": sequence(db, "payment", "RC"), "invoice": invoice["id"],
        "customer": invoice["customer"], "amount": amount, "method": method, "reference": field(data, "reference", 150),
        "at": now(), "by": actor["id"], "source": source, "academic": True})
    refresh(db, invoice)
    return paid


def account_aging(db):
    today = datetime.now(COLOMBIA).date()
    result = []
    for invoice in invoice_rows(db):
        if invoice["status"] == "RECHAZADA":
            continue
        row = invoice
        days = (today - read_date(row["due"])).days
        row.update(days_overdue=max(0, days), bucket="Al día" if days <= 0 else "1–30" if days <= 30 else "31–60" if days <= 60 else "61–90" if days <= 90 else "Más de 90")
        result.append(row)
    # Keep opening balances visible rather than silently losing the earlier ledger.
    for customer in all_records(db, "clientes"):
        balance = customer.get("finance_opening_balance", customer.get("balance", 0))
        if balance:
            due = customer.get("finance_opening_due", customer.get("due", ""))
            days = (today - read_date(due)).days if due else 0
            result.append({"id": "opening-"+customer["id"], "number": "Saldo anterior", "customer": customer["id"],
                "fiscal": {"name": customer["name"]}, "balance": balance, "customer_credit": 0, "due": due,
                "days_overdue": max(0, days), "bucket": "Al día" if days <= 0 else "1–30" if days <= 30 else "31–60" if days <= 60 else "61–90" if days <= 90 else "Más de 90", "legacy": True})
    return result


def return_order_id(row):
    return row.get("order_id", row["id"])


def report_return(db, actor, data):
    key = field(data, "request_id", 80)
    old = find(db, "retornos", key)
    if old:
        if old.get("order_id") != data.get("order"):
            raise Problem("La solicitud ya corresponde a otra devolución.", 409)
        return old
    order = require_record(db, "pedidos", data.get("order"))
    if order["status"] not in {"ENTREGADO", "CERRADO"}:
        raise Problem("Registra aquí devoluciones de pedidos entregados.", 409)
    sku, lot, location = field(data, "sku"), field(data, "lot"), field(data, "origin_location")
    qty = number(data.get("quantity"), 1)
    line = next((r for r in order["lines"] if r["sku"] == sku), None)
    reservation = next((r for r in line.get("reservations", []) if r["lot"] == lot and r["location"] == location), None) if line else None
    returned = sum(r["quantity"] for ret in all_records(db, "retornos") if return_order_id(ret) == order["id"]
                   for item in ret["lines"] if item["sku"] == sku for r in item.get("reservations", []) if r["lot"] == lot and r["location"] == location)
    if not reservation or qty + returned > reservation["quantity"]:
        raise Problem("La devolución supera las unidades del lote entregado.", 409)
    row = save(db, "retornos", {"id": key, "order_id": order["id"], "order": order["number"], "route": order.get("route", ""),
        "status": "PENDIENTE_RECEPCION", "at": now(), "note": field(data, "note", 600), "excluded_from_invoice": False, "post_delivery": True,
        "lines": [{**line, "quantity": qty, "reservations": [{**reservation, "quantity": qty}]}], "by": actor["id"]})
    if order["status"] == "CERRADO":
        save(db, "pedidos", {**order, "status": "ENTREGADO"})
    return row


def inspect_return(db, actor, data):
    row = require_record(db, "retornos", data.get("id"))
    if row["status"] != "PENDIENTE_RECEPCION":
        return row
    decision = data.get("decision")
    if decision not in {"REINGRESO", "MERMA"}:
        raise Problem("Selecciona reingreso o merma después de inspeccionar.")
    reason = field(data, "reason", 600)
    order = require_record(db, "pedidos", return_order_id(row))
    catalog = products(db)
    location = field(data, "location") if decision == "REINGRESO" else ""
    for line in row["lines"]:
        item = catalog.get(line["sku"])
        if not item:
            raise Problem("Reactiva el producto antes de inspeccionar el retorno.", 409)
        for allocation in line.get("reservations", []):
            lots = list(run_db(db, "commerce_lots", "SELECT * FROM lots WHERE product_id=? ORDER BY expiry,lot,location", (item["id"],)))
            original = next((r for r in lots if r["lot"] == allocation["lot"] and r["location"] == allocation["location"]), None)
            if not original:
                raise Problem("No se encontró el lote de origen.", 409)
            if decision == "REINGRESO":
                if original["expiry"] < datetime.now(COLOMBIA).date().isoformat():
                    raise Problem("El lote está vencido: registra merma.", 409)
                target = next((r for r in lots if r["lot"] == allocation["lot"] and r["location"] == location), None)
                if target:
                    update_lot(db, target, target["quantity"] + allocation["quantity"], target["reserved"])
                else:
                    run_db(db, "commerce_lot_add", "INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved) VALUES(?,?,?,?,?,?)",
                        (item["id"], allocation["lot"], original["expiry"], location, allocation["quantity"], 0))
    row.update(status="RECIBIDO" if decision == "REINGRESO" else "MERMA", decision=decision, reason=reason,
               received_at=now(), location=location, inspected_by=actor["id"])
    if decision == "MERMA":
        save(db, "mermas", {"id": row["id"], "order": order["id"], "lines": row["lines"], "reason": reason, "at": now()})
    invoice = invoice_for(db, order["id"])
    if invoice and invoice["status"] != "RECHAZADA" and not row.get("excluded_from_invoice", not row.get("order_id")):
        total = sum(r["quantity"] * r["price"] for r in row["lines"])
        credit = save(db, "notas_credito", {"id": row["id"], "number": sequence(db, "credit_note", "NC"), "invoice": invoice["id"],
            "total": total, "lines": row["lines"], "reason": reason, "at": now(), "academic": True})
        row["credit_note"] = credit["number"]
    save(db, "retornos", row)
    save(db, "pedidos", {**order, "return_received": now()})
    if invoice and invoice["status"] != "RECHAZADA":
        refresh(db, invoice)
    return row


def expire_stock(db, actor, data):
    key = field(data, "request_id", 80)
    previous = find(db, "mermas", key)
    if previous:
        return previous
    item = products(db).get(field(data, "sku", 80))
    if not item:
        raise Problem("Producto no encontrado.", 404)
    lot = next((r for r in run_db(db, "commerce_lots", "SELECT * FROM lots WHERE product_id=?", (item["id"],))
                if r["lot"] == data.get("lot") and r["location"] == data.get("location")), None)
    quantity = number(data.get("quantity"), 1)
    if not lot or lot["expiry"] >= datetime.now(COLOMBIA).date().isoformat():
        raise Problem("Selecciona un lote vencido para registrar esta merma.", 409)
    if quantity > lot["quantity"] - lot["reserved"]:
        raise Problem("La merma supera la existencia no reservada del lote.", 409)
    reason = field(data, "reason", 1000)
    update_lot(db, lot, lot["quantity"] - quantity, lot["reserved"])
    return save(db, "mermas", {"id": key, "order": "", "kind": "VENCIMIENTO", "reason": reason,
        "lines": [{"sku": item["sku"], "name": item["name"], "lot": lot["lot"], "location": lot["location"], "quantity": quantity}],
        "at": now(), "by": actor["id"]})


def settle_route(db, actor, data):
    route = require_record(db, "rutas", data.get("id"))
    previous = find(db, "liquidaciones", route["id"])
    if previous:
        return previous
    if route["status"] != "FINALIZADA":
        raise Problem("Finaliza las entregas de la ruta antes de liquidar.", 409)
    expected, invoices = 0, []
    for key in route["orders"]:
        order = require_record(db, "pedidos", key)
        if any(return_order_id(r) == key and r["status"] == "PENDIENTE_RECEPCION" for r in all_records(db, "retornos")):
            raise Problem("Inspecciona las devoluciones pendientes antes de liquidar.", 409)
        if order["status"] == "NOVEDAD":
            continue
        invoice = invoice_for(db, key)
        if not invoice or invoice["status"] == "RECHAZADA":
            raise Problem("Emite las facturas aceptadas de los pedidos entregados.", 409)
        if not order.get("credit"):
            row = invoice_balance(db, invoice)
            expected += row["balance"]
            invoices.append(row)
    received = number(data.get("received"))
    difference = expected - received
    statement = str(data.get("statement", "")).strip()[:1000]
    if difference and not statement:
        raise Problem("Adjunta el acta de diferencia por " + money(difference) + " antes del cierre.", 409)
    left = received
    for invoice in invoices:
        amount = min(left, invoice["balance"])
        if amount:
            payment(db, actor, {"request_id": "route-"+route["id"]+"-"+invoice["id"], "invoice": invoice["id"],
                "amount": amount, "method": "EFECTIVO", "reference": "Liquidación " + route["number"]}, "route")
            left -= amount
    row = save(db, "liquidaciones", {"id": route["id"], "number": sequence(db, "settlement", "LQ"), "route": route["number"],
        "expected": expected, "received": received, "difference": difference, "unapplied": left, "statement": statement, "at": now(), "by": actor["id"]})
    save(db, "rutas", {**route, "status": "LIQUIDADA", "settled_at": now()})
    return row


def pse_key(db):
    row = find(db, "finance_secrets", "pse")
    if not row:
        row = save(db, "finance_secrets", {"id": "pse", "key": secrets.token_hex(32)})
    return row["key"]


def confirm_pse(db, raw, timestamp, signature):
    try:
        if abs(time.time() - int(timestamp)) > 300:
            raise ValueError
    except (TypeError, ValueError):
        raise Problem("Webhook vencido o sin fecha válida.", 401)
    secret = find(db, "finance_secrets", "pse")
    expected = hmac.new((secret or {}).get("key", "").encode(), str(timestamp).encode()+b"."+raw, hashlib.sha256).hexdigest()
    if not secret or not isinstance(signature, str) or not hmac.compare_digest(signature, expected):
        raise Problem("Firma de webhook inválida.", 401)
    try:
        event = json.loads(raw)
        intent = require_record(db, "pse_intents", event["intent"])
    except (ValueError, KeyError, TypeError):
        raise Problem("Evento de pago inválido.") from None
    if event.get("amount") != intent["amount"] or event.get("result") != "CONFIRMADO":
        raise Problem("El evento no coincide con la transacción de prueba.", 409)
    if intent["status"] == "CONFIRMADO":
        return intent
    payment(db, {"id": intent["by"]}, {"request_id": "pse-"+intent["id"], "invoice": intent["invoice"],
        "amount": intent["amount"], "method": "PSE", "reference": intent["id"]}, "webhook")
    return save(db, "pse_intents", {**intent, "status": "CONFIRMADO", "confirmed_at": now()})


def dashboard(db, query):
    today = datetime.now(COLOMBIA).date()
    start = read_date(query.get("from", [today.replace(day=1).isoformat()])[0])
    end = read_date(query.get("to", [today.isoformat()])[0])
    if start.year < 1970 or end < start or (end-start).days > 1096:
        raise Problem("Selecciona un periodo válido de hasta tres años.")
    customer = query.get("customer", [""])[0]; zone = query.get("zone", [""])[0]; sku = query.get("sku", [""])[0]
    invoice_map={r["id"]:r for r in all_records(db,"facturas")}
    credit_rows=all_records(db,"notas_credito")
    customers={r["id"]:r for r in all_records(db,"clientes")}
    orders={r["id"]:r for r in all_records(db,"pedidos")}
    def selected(first, last):
        rows = []
        for inv in invoice_map.values():
            if inv["status"] == "RECHAZADA" or not first.isoformat() <= inv["issued_at"][:10] <= last.isoformat():
                continue
            if customer and inv["customer"] != customer or zone and inv["zone"] != zone:
                continue
            for line in inv["lines"]:
                if sku and line["sku"] != sku:
                    continue
                rows.append({"invoice": inv["number"], "customer_id": inv["customer"], "customer": inv["fiscal"]["name"],
                             "zone": inv["zone"], "date": inv["issued_at"][:10], **line, "total": line["price"]*line["quantity"]})
        for credit in credit_rows:
            if not first.isoformat() <= credit["at"][:10] <= last.isoformat():continue
            inv = invoice_map[credit["invoice"]]
            if customer and inv["customer"] != customer or zone and inv["zone"] != zone:continue
            for line in credit["lines"]:
                if sku and line["sku"] != sku:continue
                rows.append({"invoice":credit["number"],"customer_id":inv["customer"],"customer":inv["fiscal"]["name"],
                    "zone":inv["zone"],"date":credit["at"][:10],"sku":line["sku"],"name":line["name"],"quantity":-line["quantity"],"price":line["price"],"total":-line["price"]*line["quantity"]})
        return rows
    rows = selected(start, end)
    # Calendar-month comparison preserves October versus September even when month lengths differ.
    if start.day == 1 and end.day == calendar.monthrange(end.year, end.month)[1] and start.month == end.month and start.year == end.year:
        prev_end = start - timedelta(days=1); prev_start = prev_end.replace(day=1)
    else:
        prev_end = start-timedelta(days=1); prev_start = prev_end-timedelta(days=(end-start).days)
    previous = sum(r["total"] for r in selected(prev_start, prev_end))
    total = sum(r["total"] for r in rows)
    def ranking(key):
        values = {}
        for row in rows:
            values[row[key]] = values.get(row[key], 0) + row["total"]
        return [{"name": name, "total": value} for name,value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:10]]
    stock = []
    sold = {}
    lots_by_product={}
    for lot in run_db(db,"finance_lots","SELECT * FROM lots"):
        if not lot["lot"].startswith("DEMO-IT-"):lots_by_product.setdefault(lot["product_id"],[]).append(lot)
    for row in rows:sold[row["sku"]] = sold.get(row["sku"], 0) + row["quantity"]
    for item in run_db(db, "finance_products", "SELECT * FROM products WHERE active=1 ORDER BY name"):
        if not item["active"] or sku and item["sku"] != sku:continue
        lots = lots_by_product.get(item["id"], [])
        available = sum(r["quantity"]-r["reserved"] for r in lots if r["expiry"] >= today.isoformat())
        physical = sum(r["quantity"] for r in lots)
        stock.append({"sku":item["sku"], "name":item["name"], "available":available, "minimum":item["minimum"],
            "shortage":max(0,item["minimum"]-available), "sold_units":sold.get(item["sku"],0),
            "rotation":round(sold.get(item["sku"],0)/physical,4) if physical else None,
            "expired_units":sum(r["quantity"] for r in lots if r["expiry"] < today.isoformat())})
    losses = [r for r in all_records(db,"mermas") if start.isoformat() <= r["at"][:10] <= end.isoformat()]
    if customer:losses=[r for r in losses if orders.get(r["order"],{}).get("customer")==customer]
    if zone:losses=[r for r in losses if customers.get(orders.get(r["order"],{}).get("customer"),{}).get("zone")==zone]
    aging=[r for r in account_aging(db) if (not customer or r["customer"]==customer) and (not zone or customers[r["customer"]]["zone"]==zone)]
    return {"from":start.isoformat(), "to":end.isoformat(), "previous_from":prev_start.isoformat(), "previous_to":prev_end.isoformat(),
        "filters":{"customer":customer,"zone":zone,"sku":sku}, "sales":total,"previous_sales":previous,"variation":round((total-previous)*100/previous,2) if previous else None,
        "rows":rows,"top_customers":ranking("customer"),"top_products":ranking("name"),"top_zones":ranking("zone"),
        "stock":stock,"aging":aging,"losses":losses,"receivables":sum(r["balance"] for r in aging),"customer_credit":sum(r.get("customer_credit",0) for r in aging),
        "loss_units":sum(l["quantity"] for r in losses for l in r["lines"] if not sku or l["sku"]==sku),
        "rotation_definition":"Unidades facturadas del periodo / existencia física al consultar; no es rotación contable sobre inventario promedio.",
        "stock_scope":"Inventario actual del SKU seleccionado; no se distribuye por cliente o zona.","academic":True}


def document(db, actor, query):
    invoice = authorized_invoice(db, actor, query.get("id", [""])[0])
    fmt = query.get("format", ["pdf"])[0]
    if fmt == "xml":
        root = Element("AcademicInvoice", number=invoice["number"], fiscalValidity="none")
        for key,value in (("Notice",ACADEMIC),("CUFE",invoice.get("cufe","")),("Customer",invoice["fiscal"]["name"]),("NIT",invoice["fiscal"]["nit"]),("TotalCents",str(invoice["total"]))):SubElement(root,key).text=value
        for line in invoice["lines"]:SubElement(root,"Line",sku=line["sku"],quantity=str(line["quantity"]),priceCents=str(line["price"]))
        return tostring(root,encoding="utf-8",xml_declaration=True),"application/xml",invoice["number"]+".xml"
    if fmt != "pdf":raise Problem("Selecciona PDF o XML.")
    return make_pdf(invoice["number"], [[l["sku"],l["name"],l["quantity"],money(l["price"]),money(l["price"]*l["quantity"])] for l in invoice["lines"]],
                    ["SKU","Producto","Cantidad","Precio","Total"], [invoice["fiscal"]["name"],invoice["fiscal"]["nit"],"Estado: "+invoice["status"],"CUFE de prueba: "+invoice.get("cufe","No aceptada"),"Total: "+money(invoice["total"])]),"application/pdf",invoice["number"]+".pdf"


def make_pdf(title, rows, headers, notes=()):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from xml.sax.saxutils import escape
    buf=BytesIO(); styles=getSampleStyleSheet(); parts=[Paragraph(escape(title),styles["Title"]),Paragraph(ACADEMIC,styles["Normal"]),Spacer(1,12)]
    parts.extend(Paragraph(escape(str(n)),styles["Normal"]) for n in notes)
    values=[[Paragraph(escape(str(c)),styles["Normal"]) for c in row] for row in [headers]+rows]
    from reportlab.lib.pagesizes import A4, landscape
    page=landscape(A4) if len(headers)>6 else A4
    table=Table(values,colWidths=[(page[0]-144)/len(headers)]*len(headers),repeatRows=1,hAlign="LEFT");table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor('#dfebdf')),("VALIGN",(0,0),(-1,-1),'TOP'),("GRID",(0,0),(-1,-1),.3,colors.lightgrey)]));parts.extend([Spacer(1,12),table]);SimpleDocTemplate(buf,pagesize=page).build(parts);return buf.getvalue()


def export_dashboard(report, fmt):
    headers=["Factura","Fecha","Cliente","Zona","SKU","Producto","Cantidad","Precio centavos","Total centavos"]
    values=[[r[k] for k in ("invoice","date","customer","zone","sku","name","quantity","price","total")] for r in report["rows"]]
    if fmt=="pdf":return make_pdf("Ventas filtradas",values,headers,[str(report["filters"]),report["from"]+" a "+report["to"]]),"application/pdf","Indicadores.pdf"
    if fmt!="xlsx":raise Problem("Selecciona Excel o PDF.")
    from openpyxl import Workbook
    book=Workbook();sheet=book.active;sheet.title="Ventas filtradas";sheet.append([ACADEMIC]);sheet.append(["Desde",report["from"],"Hasta",report["to"]]);sheet.append(["Filtros",json.dumps(report["filters"],ensure_ascii=False)]);sheet.append(["Ventas centavos",report["sales"],"Periodo anterior",report["previous_sales"]]);sheet.append(headers)
    for row in values:sheet.append([("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for v in row])
    sheet.freeze_panes="A6";sheet.auto_filter.ref=f"A5:I{max(5,sheet.max_row)}"
    for col,width in zip('ABCDEFGHI',[24,14,32,20,22,40,12,22,22]):sheet.column_dimensions[col].width=width
    summary=book.create_sheet("Resumen");summary.append(["Indicador","Valor"])
    for key,label in (("sales","Ventas netas centavos"),("previous_sales","Periodo anterior centavos"),("variation","Variación porcentual"),("receivables","Cartera actual centavos"),("customer_credit","Saldo a favor centavos"),("loss_units","Unidades a merma")):
        summary.append([label,report[key]])
    summary.append(["Periodo",report["from"]+" a "+report["to"]]);summary.append(["Comparación",report["previous_from"]+" a "+report["previous_to"]]);summary.append(["Alcance inventario",report["stock_scope"]]);summary.append(["Relación venta/stock",report["rotation_definition"]])
    inventory=book.create_sheet("Inventario");inventory.append(["SKU","Producto","Disponible","Mínimo","Faltante","Unidades facturadas","Relación venta/stock","Vencidas"])
    for r in report["stock"]:inventory.append([r[k] for k in ("sku","name","available","minimum","shortage","sold_units","rotation","expired_units")])
    aging=book.create_sheet("Cartera actual");aging.append(["Documento","Cliente","Vencimiento","Edad","Saldo centavos","Saldo a favor centavos"])
    for r in report["aging"]:aging.append([r["number"],r["fiscal"]["name"],r["due"],r["bucket"],r["balance"],r.get("customer_credit",0)])
    rankings=book.create_sheet("Rankings");rankings.append(["Agrupación","Nombre","Total centavos"])
    for key,label in (("top_customers","Cliente"),("top_products","Producto"),("top_zones","Zona")):
        for r in report[key]:rankings.append([label,r["name"],r["total"]])
    losses=book.create_sheet("Mermas");losses.append(["Fecha","Pedido","Motivo","SKU","Unidades"])
    for r in report["losses"]:
        for line in r["lines"]:
            if not report["filters"]["sku"] or line["sku"]==report["filters"]["sku"]:losses.append([r["at"],r["order"],r["reason"],line["sku"],line["quantity"]])
    from openpyxl.styles import Font, PatternFill, Alignment
    for view in book:
        first=5 if view==sheet else 1
        for cell in view[first]:cell.font=Font(bold=True,color="FFFFFF");cell.fill=PatternFill("solid",fgColor="234B37")
        for cells in view.iter_rows():
            for cell in cells:
                if isinstance(cell.value,str) and cell.value.startswith(('=','+','-','@')):cell.value="'"+cell.value
                cell.alignment=Alignment(vertical="top",wrap_text=True)
        if view!=sheet:
            view.freeze_panes="A2"
            for column in view.columns:view.column_dimensions[column[0].column_letter].width=min(60,max(18,max(len(str(c.value or '')) for c in column)+2))
        view.sheet_properties.pageSetUpPr.fitToPage=True
    buf=BytesIO();book.save(buf);return buf.getvalue(),"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","Indicadores.xlsx"


def authorized_invoice(db, actor, key):
    row=require_record(db,"facturas",key)
    if actor["role"]=="10":
        customer=sale_customer(db,actor)
        if not customer or row["customer"]!=customer["id"]:raise Problem("Factura no encontrada.",404)
    return row


def webhook(handler, db):
    raw=handler.body(16384)
    with transaction(db):
        result=confirm_pse(db,raw,handler.headers.get('X-PSE-Timestamp'),handler.headers.get('X-PSE-Signature'))
        audit(db,"pasarela-simulada","PSE_CONFIRMADO",handler.ip,result["id"])
    return handler.respond({"id":result["id"],"status":result["status"],"academic":True})


def dispatch(handler, db, actor, method, kind, query):
    handler.require(db,actor,ROLES.get(kind,set()),"/api/finanzas/"+kind)
    if method=="GET":
        if kind=="nota-credito":
            credit=require_record(db,"notas_credito",query.get("id",[""])[0]);inv=authorized_invoice(db,actor,credit["invoice"])
            content=make_pdf(credit["number"],[[r["sku"],r["quantity"],money(r["price"]*r["quantity"])] for r in credit["lines"]],["SKU","Cantidad","Valor"],["Factura: "+inv["number"],credit["reason"],"Total: "+money(credit["total"])])
            return handler.respond(content,content_type="application/pdf",Content_Disposition=f'attachment; filename="{credit["number"]}.pdf"')
        if kind=="acta-ruta":
            row=require_record(db,"liquidaciones",query.get("id",[""])[0]);content=make_pdf(row["number"],[[row["route"],money(row["expected"]),money(row["received"]),money(row["difference"])]],["Ruta","Esperado","Recibido","Diferencia"],[row["at"],row["statement"] or "Recaudo conciliado sin diferencia."])
            return handler.respond(content,content_type="application/pdf",Content_Disposition=f'attachment; filename="{row["number"]}.pdf"')
        if kind=="documento":
            content,mime,name=document(db,actor,query);return handler.respond(content,content_type=mime,Content_Disposition=f'attachment; filename="{name}"')
        if kind=="indicadores":
            cut=query.get("cut",[""])[0]
            result={**require_record(db,"indicadores_materializados",cut)["report"],"materialized_at":require_record(db,"indicadores_materializados",cut)["at"]} if cut else dashboard(db,query)
            if query.get('format'):
                content,mime,name=export_dashboard(result,query['format'][0]);return handler.respond(content,content_type=mime,Content_Disposition=f'attachment; filename="{name}"')
            return handler.respond({**result,"customers":[{"id":r['id'],"name":r['name'],"zone":r['zone']} for r in all_records(db,'clientes')],"products":list(products(db).values())})
        if kind=="cortes":return handler.respond({"rows":[{k:r[k] for k in ('id','at','from','to','filters','sales')} for r in all_records(db,'indicadores_materializados')]})
        if kind=="cartera":return handler.respond({"rows":account_aging(db),"academic":True})
        invoices=invoice_rows(db)
        if actor['role']=='10':
            customer=sale_customer(db,actor);invoices=[r for r in invoices if customer and r['customer']==customer['id']]
        if kind in {'facturas','pagos','pse'}:
            allowed={r['id'] for r in invoices}
            opening=[r for r in account_aging(db) if r.get("legacy")] if actor["role"]=="09" else []
            allowed.update(r["id"] for r in opening)
            orders=[{k:r[k] for k in ('id','number','customer','customer_name','total')} for r in all_records(db,'pedidos') if r['status'] in {'ENTREGADO','CERRADO'}] if actor['role']=='09' else []
            return handler.respond({"rows":invoices,"opening":opening,"orders":orders,"payments":[r for r in all_records(db,'pagos') if r['invoice'] in allowed],"intents":[r for r in all_records(db,'pse_intents') if r['invoice'] in allowed],"fiscal":all_records(db,'fiscal_customers') if actor['role']=='09' else [],"academic":True})
        if kind=='liquidaciones':return handler.respond({"rows":all_records(db,'liquidaciones'),"routes":[{**r,"cash_expected":sum(invoice_balance(db,inv)['balance'] for key in r['orders'] if (inv:=invoice_for(db,key)) and inv['status']!='RECHAZADA' and not require_record(db,'pedidos',key).get('credit'))} for r in all_records(db,'rutas') if r['status']=='FINALIZADA']})
        if kind=='devoluciones':
            catalog={r['id']:r for r in run_db(db,'finance_products','SELECT * FROM products WHERE active=1 ORDER BY name')}
            expired=[{**dict(r),'sku':catalog[r['product_id']]['sku'],'name':catalog[r['product_id']]['name']} for r in run_db(db,'finance_lots','SELECT * FROM lots') if r['product_id'] in catalog and r['expiry']<datetime.now(COLOMBIA).date().isoformat() and r['quantity']>r['reserved']]
            return handler.respond({"rows":all_records(db,'retornos'),"credits":all_records(db,'notas_credito'),"expired":expired,"losses":all_records(db,'mermas'),"orders":[r for r in all_records(db,'pedidos') if r['status'] in {'ENTREGADO','CERRADO'}]})
        if kind=='bandeja':return handler.respond({"rows":all_records(db,'bandeja_facturas'),"academic":True})
        raise Problem("Página no encontrada.",404)
    if method!='POST':raise Problem("Método no permitido.",405)
    data=handler.data()
    with transaction(db):
        current=run_db(db,'user_by_id','SELECT * FROM users WHERE id=?',(actor['id'],)).fetchone()
        if not current or not current['active'] or current['role']!=actor['role']:raise Problem("Inicia sesión de nuevo.",401)
        if kind=='facturas' and actor['role']=='09':result=emit_invoice(db,actor,data)
        elif kind=='indicadores' and data.get('action')=='snapshot':
            key=field(data,'request_id',80);params={k:[str(data[k])] for k in ('from','to','customer','zone','sku') if k in data}
            previous=find(db,'indicadores_materializados',key)
            if previous:
                if previous['params']!=params:raise Problem("El corte ya corresponde a otros filtros.",409)
                result={k:previous[k] for k in ('id','at','sales')}
            else:
                report=dashboard(db,params);row=save(db,'indicadores_materializados',{'id':key,'at':now(),'from':report['from'],'to':report['to'],'filters':report['filters'],'params':params,'sales':report['sales'],'report':report,'by':actor['id']})
                result={k:row[k] for k in ('id','at','sales')}
        elif kind=='pagos' and actor['role']=='09':result=payment(db,actor,data)
        elif kind=='liquidaciones':result=settle_route(db,actor,data)
        elif kind=='devoluciones':
            result=report_return(db,actor,data) if data.get('action')=='report' else inspect_return(db,actor,data) if data.get('action')=='inspect' else expire_stock(db,actor,data) if data.get('action')=='expiry' else None
            if result is None:raise Problem("Selecciona registrar o inspeccionar devolución.")
        elif kind=='pse':
            if data.get('action')=='start':
                inv=authorized_invoice(db,actor,data.get('invoice'));balance=invoice_balance(db,inv)['balance'];amount=number(data.get('amount'),1)
                if inv['status']=='RECHAZADA' or amount>balance:raise Problem("Revisa el saldo de la factura aceptada.",409)
                pse_key(db);result=save(db,'pse_intents',{'id':uuid4().hex,'invoice':inv['id'],'amount':amount,'by':actor['id'],'status':'PENDIENTE','at':now(),'academic':True})
            elif data.get('action')=='simulate':
                intent=require_record(db,'pse_intents',data.get('id'));authorized_invoice(db,actor,intent['invoice'])
                stamp=str(int(time.time()));raw=json.dumps({'intent':intent['id'],'amount':intent['amount'],'result':'CONFIRMADO'}).encode()
                signature=hmac.new(pse_key(db).encode(),stamp.encode()+b'.'+raw,hashlib.sha256).hexdigest();result=confirm_pse(db,raw,stamp,signature)
            else:raise Problem("Selecciona iniciar o confirmar PSE de prueba.")
        else:raise Problem("Acceso denegado.",403)
        audit(db,actor['username'],'FINANZAS_'+kind.upper(),handler.ip,str(result.get('id','')))
    return handler.respond(result)
