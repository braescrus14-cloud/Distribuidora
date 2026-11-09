"""Restaura el catálogo y los lotes de una instalación local en PostgreSQL."""

import argparse
from contextlib import closing
from getpass import getpass
import json
from pathlib import Path
import sqlite3

from app import PostgresDatabase, audit, initialize_schema, transaction


def restore(db, source, sku_map):
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as local:
        local.row_factory = sqlite3.Row
        local.execute("BEGIN")
        products = local.execute("SELECT * FROM products ORDER BY id").fetchall()
        catalog = local.execute("SELECT * FROM catalog_sources").fetchall()
        lots = local.execute("SELECT * FROM lots").fetchall()
        initial = local.execute("SELECT * FROM imports WHERE id=1").fetchone()
    product_ids = {}
    with transaction(db):
        for row in products:
            sku = sku_map.get(row["barcode"], row["sku"])
            existing = db.execute("SELECT id,sku,barcode FROM products WHERE sku=? OR barcode=?",
                                  (sku, row["barcode"])).fetchall()
            if existing:
                if len(existing) != 1 or existing[0]["barcode"] != row["barcode"]:
                    raise ValueError(f"El SKU {sku} coincide con un producto diferente.")
                product_ids[row["id"]] = existing[0]["id"]
                continue
            fields = ("barcode", "name", "brand", "species", "presentation", "price_cents", "minimum", "active")
            product_ids[row["id"]] = db.execute("""INSERT INTO products
                (sku,barcode,name,brand,species,presentation,price_cents,minimum,active)
                VALUES(?,?,?,?,?,?,?,?,?) RETURNING id""", (sku, *(row[field] for field in fields))).fetchone()["id"]
        for row in catalog:
            db.execute("""INSERT INTO catalog_sources(product_id,source_key,price_status) VALUES(?,?,?)
                ON CONFLICT(product_id) DO NOTHING""",
                (product_ids[row["product_id"]], row["source_key"], row["price_status"]))
        previous = db.execute("SELECT digest FROM imports WHERE id=1").fetchone()
        if previous and initial and previous["digest"] != initial["digest"]:
            raise ValueError("La base de destino ya tiene una carga inicial distinta.")
        for row in lots:
            if row["lot"].startswith("DEMO-IT-"):
                continue
            fields = ("expiry", "quantity", "reserved")
            values = tuple(row[field] for field in fields)
            key = (product_ids[row["product_id"]], row["lot"], row["location"])
            existing = db.execute("""SELECT expiry,quantity,reserved FROM lots
                WHERE product_id=? AND lot=? AND location=?""", key).fetchone()
            if existing:
                if tuple(existing[field] for field in fields) != values:
                    raise ValueError(f"El lote {row['lot']} ya existe con otros datos.")
                continue
            db.execute("""INSERT INTO lots(product_id,lot,location,expiry,quantity,reserved)
                VALUES(?,?,?,?,?,?)""", (*key, *values))
        if initial and not previous:
            db.execute("INSERT INTO imports VALUES(1,?,?)", (initial["digest"], initial["row_count"]))
        confirmed = [row for row in lots if not row["lot"].startswith("DEMO-IT-")]
        if not previous:
            audit(db, "sistema", "RESTAURACION_POSTGRES", "local",
                  f"{len(products)} productos y {len(confirmed)} lotes de la copia local")
    return len(products), len(confirmed), sum(row["quantity"] for row in confirmed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origen", type=Path, default=Path("C:/Distribuidora/Sprint1/villali.sqlite3"))
    parser.add_argument("--sku-map", type=Path, default=Path(__file__).with_name("sku_render.json"))
    args = parser.parse_args()
    if not args.origen.is_file():
        parser.error("No se encontró el archivo SQLite de origen.")
    mapping = json.loads(args.sku_map.read_text(encoding="utf-8")) if args.sku_map.is_file() else {}
    url = getpass("Pega la cadena de conexión PostgreSQL de Neon: ").strip()
    if not url.startswith(("postgresql://", "postgres://")):
        parser.error("Se requiere una cadena de conexión PostgreSQL.")
    from psycopg.conninfo import make_conninfo

    db = None
    try:
        db = PostgresDatabase(make_conninfo(url, sslmode="require"))
        initialize_schema(db)
        products, lots, units = restore(db, args.origen, mapping)
        print(f"Restauración verificada: {products} productos, {lots} lotes y {units} unidades.")
    except (sqlite3.Error, ValueError):
        print("No se completó la restauración. Revisa si el destino contiene productos o lotes distintos.")
        return 1
    except Exception:
        print("No se pudo acceder a PostgreSQL. Revisa la cadena de conexión y el estado de Neon.")
        return 1
    finally:
        if db is not None:
            db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
