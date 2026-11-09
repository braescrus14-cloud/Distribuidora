"""Carga el catálogo Italcol de Excel sin convertirlo en inventario físico."""

import argparse
from decimal import Decimal
import hashlib
from pathlib import Path
import re
import unicodedata

from openpyxl import load_workbook

from app import SCHEMA, audit, database, transaction


def canonical(value):
    text = re.sub(r"\s*\(fase [^)]+\)", "", value.casefold())
    return "".join(c for c in unicodedata.normalize("NFKD", text) if c.isalnum())


def read_catalog(path):
    book = load_workbook(path, read_only=True, data_only=True, keep_links=False)
    try:
        rows = book["CATÁLOGO ITALCOL"].iter_rows(min_row=6, max_col=5, values_only=True)
        if next(rows)[:4] not in {
            ("LÍNEA", "PRODUCTO OFICIAL", "PRESENTACIÓN VERIFICADA", "PRECIO (COP)"),
            ("LÍNEA", "PRODUCTO ITALCOL", "PRESENTACIÓN / BASE", "PRECIO REF. (COP)"),
        }:
            raise ValueError("Los encabezados del catálogo no coinciden.")
        entries = {}
        for number, (line, name, presentation, price, status) in enumerate(rows, 7):
            if not line and not name:
                continue
            if not isinstance(line, str) or not isinstance(name, str) or not isinstance(status, str):
                raise ValueError(f"Fila {number}: faltan datos de catálogo.")
            key = canonical(line) + ":" + canonical(name)
            if key in entries:
                raise ValueError(f"Fila {number}: referencia duplicada.")
            cents = Decimal(str(price)) * 100 if price is not None else 0
            if cents < 0 or cents != int(cents):
                raise ValueError(f"Fila {number}: precio inválido.")
            entries[key] = (line, name, presentation or "", int(cents), status)
        return entries
    finally:
        book.close()


def identifier(key):
    fingerprint = hashlib.sha256(key.encode()).hexdigest()
    base = f"201{int(fingerprint[:12], 16) % 10**9:09d}"
    check = -sum(int(digit) * (1 if index % 2 == 0 else 3)
                 for index, digit in enumerate(base)) % 10
    return f"ITAL-XLS-{fingerprint[:12].upper()}", base + str(check)


def import_catalog(path):
    entries = read_catalog(path)
    counts = dict(new=0, matched=0, updated=0, unchanged=0)
    with database() as db:
        db.executescript(SCHEMA)
        with transaction(db):
            demos = {canonical(row["name"]): row["id"] for row in db.execute(
                "SELECT id,name FROM products WHERE sku LIKE 'DEMO-IT-%'")}
            imported = {row["source_key"]: row for row in db.execute("""SELECT p.id,p.name,p.presentation,
                p.price_cents,c.source_key,c.price_status FROM catalog_sources c
                JOIN products p ON p.id=c.product_id""")}
            for key, (line, name, presentation, price, status) in entries.items():
                if key in imported:
                    old = imported[key]
                    if (old["name"], old["presentation"], old["price_cents"], old["price_status"]) == (name, presentation, price, status):
                        counts["unchanged"] += 1
                    else:
                        db.execute("UPDATE products SET name=?,presentation=?,price_cents=? WHERE id=?",
                                   (name, presentation, price, old["id"]))
                        db.execute("UPDATE catalog_sources SET price_status=? WHERE product_id=?", (status, old["id"]))
                        counts["updated"] += 1
                    continue
                product_id = demos.pop(canonical(name), None)
                if product_id is None:
                    sku, barcode = identifier(key)
                    product_id = db.execute("""INSERT INTO products
                        (sku,barcode,name,brand,species,presentation,price_cents,minimum)
                        VALUES(?,?,?,'Italcol',?,?,?,10)""",
                        (sku, barcode, name, line, presentation, price)).lastrowid
                    counts["new"] += 1
                else:
                    db.execute("UPDATE products SET name=?,presentation=?,price_cents=? WHERE id=?",
                               (name, presentation, price, product_id))
                    counts["matched"] += 1
                db.execute("INSERT INTO catalog_sources VALUES(?,?,?)", (product_id, key, status))
            if counts["new"] or counts["matched"] or counts["updated"]:
                audit(db, "sistema", "CATALOGO_EXCEL", "local", f"{len(entries)} referencias")
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("excel", type=Path)
    args = parser.parse_args()
    print(import_catalog(args.excel))
