from datetime import datetime, timedelta

from app import run_db, transaction
from commerce import COLOMBIA, accounts, find, nit_digit, products, save


def seed(db):
    with transaction(db):
        if find(db, "settings", "commerce-v1"):
            return
        expiry = (datetime.now(COLOMBIA).date() + timedelta(days=300)).isoformat()
        items = (
            ("VIL-CAN-15", "2050000001017", "Alimento canino adulto 15 kg", "Caninos", "15 kg", 9750000, 50),
            ("VIL-FEL-08", "2050000001024", "Alimento felino adulto 8 kg", "Felinos", "8 kg", 7450000, 24),
            ("VIL-AVI-40", "2050000001031", "Alimento para aves de postura 40 kg", "Aves de postura", "40 kg", 12100000, 0),
        )
        existing = products(db)
        for sku, barcode, name, species, presentation, price, quantity in items:
            if sku in existing:
                continue
            product = run_db(db, "product_add", """INSERT INTO products
                (sku,barcode,name,brand,species,presentation,price_cents,minimum)
                VALUES(?,?,?,?,?,?,?,?) RETURNING id""",
                (sku, barcode, name, "Villali", species, presentation, price, 5)).fetchone()
            if quantity:
                run_db(db, "commerce_lot_add", """INSERT INTO lots(product_id,lot,expiry,location,quantity,reserved)
                    VALUES(?,?,?,?,?,?)""", (product["id"], f"L-{sku}", expiry, "Bodega principal", quantity, 0))
        for nit, name, contact, skus in (
            ("901763482", "Nutrición del Valle", "Mariana Solano", [items[0][0], items[1][0]]),
            ("901763483", "Suministros La Cumbre", "Diego Herrera", [items[2][0]]),
        ):
            key = f"{nit}-{nit_digit(nit)}"
            if not find(db, "proveedores", key):
                save(db, "proveedores", {"id": key, "name": name, "contact": contact, "skus": skus,
                                          "terms": "30 días", "active": True})
        roles = accounts(db)
        advisor = next((row["id"] for row in roles if row["role"] == "06"), 0)
        portal = next((row["id"] for row in roles if row["role"] == "10"), 0)
        customers = (
            ("alto-verde", "Agropecuaria Alto Verde", "Norte", "mayorista", "A", 300_000_000, 0, "", portal),
            ("la-pradera", "Veterinaria La Pradera", "Centro", "minorista", "B", 100_000_000, 0, "", 0),
            ("monte-claro", "Agroinsumos Monte Claro", "Sur", "mayorista", "A", 200_000_000, 20_000_000,
             (datetime.now(COLOMBIA).date() - timedelta(days=45)).isoformat(), 0),
        )
        for key, name, zone, kind, price_list, credit, balance, due, account in customers:
            save(db, "clientes", {"id": key, "name": name, "zone": zone, "type": kind, "price_list": price_list,
                                   "credit": credit, "balance": balance, "due": due, "account": account,
                                   "advisor": advisor, "consent": True, "active": True})
        save(db, "settings", {"id": "commerce-v1"})
