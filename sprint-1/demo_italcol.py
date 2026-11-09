"""Carga idempotente de referencias de Italcol con existencias simuladas."""

from datetime import date, timedelta

from app import SCHEMA, audit, database, transaction


# Nombres y líneas tomados de https://italcol.com/tus-lineas-de-productos-colombia/
# Códigos, valores, presentaciones sin ficha y existencias son de demostración.
PRODUCTS = (
    ("POST", "Ital Huevo", "Aves de postura", "Bulto", 94000),
    ("POST", "Polla Levante", "Aves de postura", "Bulto", 89000),
    ("PORC", "Cerdo Engorde Naranja 360", "Porcinos", "Bulto", 91000),
    ("PORC", "Cerda Lactancia Naranja", "Porcinos", "Bulto", 112000),
    ("POLL", "Pollo Engorde", "Pollos de engorde", "Bulto", 102000),
    ("POLL", "Italpollo Campesino", "Pollos de engorde", "Bulto", 97000),
    ("BOV", "Ital Leche", "Bovinos", "Bulto", 88000),
    ("BOV", "Ital Leche 4500", "Bovinos", "Bulto", 104000),
    ("EQU", "Brío Energy", "Equinos", "Bulto", 137000),
    ("EQU", "Brío Potros", "Equinos", "Bulto", 129000),
    ("ACUI", "Aquatilapia 30", "Peces", "Saco", 141000),
    ("ACUI", "Aquatrucha Levante 45", "Peces", "Saco", 158000),
    ("SAL", "Italsal Terneros", "Bovinos", "Saco", 79000),
    ("SAL", "Italsal Cría", "Bovinos", "Saco", 83000),
    ("PEQ", "Codorniz Preiniciador", "Codornices", "Saco", 92000),
    ("PEQ", "Conejos", "Conejos", "Saco", 87000),
    ("PEQ", "Italcuyes", "Cuyes", "Saco", 76000),
    ("PEQ", "Italovinos Crecimiento", "Ovinos", "Saco", 98000),
    ("PEQ", "Pavo Iniciación", "Pavos", "Bulto", 105000),
    ("PEQ", "Pavo Engorde", "Pavos", "Bulto", 99000),
    ("EQU", "Brío Performance", "Equinos", "Bulto", 146000),
    ("EQU", "Brío Yeguas", "Equinos", "Bulto", 132000),
    ("ACUI", "Aquatilapia 32", "Peces", "Saco", 145000),
    ("ACUI", "Aquatrucha Iniciación 50", "Peces", "Saco", 164000),
)


def code_for(number):
    base = f"2000009{number:05d}"
    check = -sum(int(digit) * (1 if index % 2 == 0 else 3)
                 for index, digit in enumerate(base)) % 10
    return base + str(check)


def seed():
    products = lots = 0
    today = date.today()
    with database() as db:
        db.executescript(SCHEMA)
        with transaction(db):
            real_inventory = db.execute("SELECT 1 FROM imports WHERE id=1").fetchone()
            for number, (line, name, species, presentation, price) in enumerate(PRODUCTS, 1):
                sku = f"DEMO-IT-{line}-{number:02d}"
                row = db.execute("SELECT id FROM products WHERE sku=?", (sku,)).fetchone()
                if row:
                    continue
                product_id = db.execute("""INSERT INTO products
                    (sku,barcode,name,brand,species,presentation,price_cents,minimum)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (sku, code_for(number), name, "Italcol", species, presentation, price * 100, 10)
                ).lastrowid
                products += 1
                if not real_inventory:
                    for index, days in enumerate((18 + number % 9, 44 + number % 12, 94 + number), 1):
                        db.execute("""INSERT INTO lots(product_id,lot,expiry,location,quantity)
                            VALUES(?,?,?,?,?)""",
                            (product_id, f"DEMO-IT-{number:02d}-{index}",
                             (today + timedelta(days=days)).isoformat(),
                             f"Zona {line} · Estante {index:02d}", 12 + (number * index * 7) % 68))
                        lots += 1
            if products:
                audit(db, "sistema", "DATOS_DEMOSTRACION", "local",
                      f"Italcol: {products} referencias y {lots} lotes simulados")
    return products, lots


if __name__ == "__main__":
    products, lots = seed()
    print(f"Nuevas referencias: {products}. Nuevos lotes de demostración: {lots}.")
