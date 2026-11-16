import argparse
from getpass import getpass
import json
from pathlib import Path

from app import audit
from mongo_store import MongoDatabase
from pymongo import ReturnDocument
from restaurar_postgres import read_source


def restore_mongo(db, source, mapping):
    products, sources, lots, initial = read_source(source)
    lots = [row for row in lots if not row["lot"].startswith("DEMO-IT-")]
    with db.transaction():
        session = db.session
        current = db.many("products", {})
        by_barcode = {row["barcode"]: row for row in current}
        by_sku = {row["sku"]: row["barcode"] for row in current}
        previous = db.one("imports", {"id": 1})
        if previous and initial and previous["digest"] != initial["digest"]:
            raise ValueError("El destino ya tiene una carga inicial distinta.")
        product_ids = {}
        new = []
        for row in products:
            sku = mapping.get(row["barcode"], row["sku"])
            if sku in by_sku and by_sku[sku] != row["barcode"]:
                raise ValueError(f"El SKU {sku} ya pertenece a otro producto.")
            existing = by_barcode.get(row["barcode"])
            if existing:
                product_ids[row["id"]] = existing["id"]
            else:
                new.append({**dict(row), "sku": sku})
        if new:
            counter = db.db.counters.find_one_and_update(
                {"_id": "products"}, {"$inc": {"value": len(new)}}, upsert=True,
                return_document=ReturnDocument.AFTER, session=session)
            for number, row in enumerate(new, counter["value"] - len(new) + 1):
                product_ids[row["id"]] = number
                row["id"] = number
            db.db.products.insert_many(new, session=session)
        existing_sources = {row["product_id"] for row in db.many("catalog_sources", {})}
        missing_sources = [{**dict(row), "product_id": product_ids[row["product_id"]]}
                           for row in sources if product_ids[row["product_id"]] not in existing_sources]
        if missing_sources:
            db.db.catalog_sources.insert_many(missing_sources, session=session)
        lot_key = lambda row: (row["product_id"], row["lot"], row["location"])
        current_lots = {lot_key(row): row for row in db.many("lots", {})}
        missing_lots = []
        for row in lots:
            restored = {**dict(row), "product_id": product_ids[row["product_id"]]}
            existing = current_lots.get(lot_key(restored))
            if existing and existing != restored:
                raise ValueError(f"El lote {row['lot']} ya existe con otros datos.")
            if not existing:
                missing_lots.append(restored)
        if missing_lots:
            db.db.lots.insert_many(missing_lots, session=session)
        if initial and not previous:
            db.insert("imports", initial)
        if new or missing_lots or (initial and not previous):
            audit(db, "sistema", "RESTAURACION_INVENTARIO", "local",
                  f"{len(products)} productos y {len(lots)} lotes de la copia local")
    return len(products), len(lots), sum(row["quantity"] for row in lots)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origen", type=Path, default=Path("C:/Distribuidora/Sprint1/villali.sqlite3"))
    parser.add_argument("--sku-map", type=Path, default=Path(__file__).with_name("sku_render.json"))
    args = parser.parse_args()
    if not args.origen.is_file():
        parser.error("No se encontró la base SQLite de origen.")
    mapping = json.loads(args.sku_map.read_text(encoding="utf-8")) if args.sku_map.is_file() else {}
    uri = getpass("Pega la URI de MongoDB Atlas: ").strip()
    if not uri.startswith("mongodb+srv://"):
        parser.error("Copia la URI de Atlas que empieza por mongodb+srv://.")
    try:
        db = MongoDatabase(uri, "villali")
        db.initialize()
        products, lots, units = restore_mongo(db, args.origen, mapping)
    except ValueError as error:
        print(f"No se completó la restauración. {error}")
        return 1
    except Exception:
        print("No se pudo restaurar. Revisa la URI, el usuario de Atlas y el acceso de red desde este equipo.")
        return 1
    print(f"Restauración verificada: {products} productos, {lots} lotes y {units} unidades.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
