"""MongoDB storage for the Villali HTTP application's named operations."""

from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
import re
import sqlite3
from threading import RLock

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


@lru_cache(maxsize=2)
def client_for(uri):
    return MongoClient(uri, serverSelectionTimeoutMS=12000, appname="Villali")


class Result(list):
    def __init__(self, rows=(), rowcount=0):
        super().__init__(rows)
        self.rowcount = rowcount

    def fetchone(self):
        return self[0] if self else None

    def fetchall(self):
        return self


def like(pattern):
    return re.compile(re.escape(pattern).replace("%", ".*").replace("_", "."), re.IGNORECASE)


def fields(row, names):
    return {name: row[name] for name in names}


class MongoDatabase:
    writer = RLock()
    product_fields = ("sku", "barcode", "name", "brand", "species", "presentation", "price_cents", "minimum")
    inventory_fields = ("id", "sku", "name", "barcode", "species")

    def __init__(self, uri, name):
        self.client = client_for(uri)
        self.db = self.client[name]
        self.session = None

    def initialize(self):
        indexes = {
            "users": ["id", "username"], "products": ["id", "sku", "barcode"],
            "sessions": ["token"], "invitations": ["token", "user_id"],
            "user_contacts": ["user_id"], "catalog_sources": ["product_id", "source_key"],
            "imports": ["id"], "audit": ["id"],
        }
        for collection, keys in indexes.items():
            for key in keys:
                self.db[collection].create_index(key, unique=True)
        self.db.lots.create_index([("product_id", 1), ("lot", 1), ("location", 1)], unique=True)
        self.db.lots.create_index([("product_id", 1), ("expiry", 1)])
        self.db.counters.update_one({"_id": "write_lock"}, {"$setOnInsert": {"value": 0}}, upsert=True)

    @contextmanager
    def transaction(self):
        with self.writer, self.client.start_session() as session:
            self.session = session
            try:
                with session.start_transaction():
                    self.db.counters.update_one({"_id": "write_lock"}, {"$inc": {"value": 1}}, session=session)
                    yield
            finally:
                self.session = None

    def one(self, collection, query):
        return self.db[collection].find_one(query, {"_id": 0}, session=self.session)

    def many(self, collection, query, order=(), limit=0, skip=0):
        cursor = self.db[collection].find(query, {"_id": 0}, session=self.session)
        if order:
            cursor.sort(list(order))
        return list(cursor.skip(skip).limit(limit))

    def insert(self, collection, row):
        self.db[collection].insert_one(dict(row), session=self.session)

    def numbered(self, collection, row):
        counter = self.db.counters.find_one_and_update(
            {"_id": collection}, {"$inc": {"value": 1}}, upsert=True,
            return_document=ReturnDocument.AFTER, session=self.session,
        )
        item = {"id": counter["value"], **row}
        self.insert(collection, item)
        return item["id"]

    def update(self, collection, query, values, upsert=False):
        result = self.db[collection].update_one(query, {"$set": values}, upsert=upsert, session=self.session)
        return Result(rowcount=result.matched_count)

    def delete(self, collection, query):
        self.db[collection].delete_many(query, session=self.session)
        return Result()

    def run(self, operation, args):
        try:
            return self._run(operation, args)
        except DuplicateKeyError as error:
            raise sqlite3.IntegrityError("Registro duplicado") from error

    def _run(self, op, p):
        row = None
        if op == "health":
            self.db.command("ping")
        elif op == "audit_add":
            self.numbered("audit", {**dict(zip(("actor", "event", "ip", "detail"), p)),
                                    "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        elif op == "audit_list":
            return Result(self.many("audit", {}, [("id", -1)], limit=100))
        elif op == "session_user":
            current = self.one("sessions", {"token": p[0]})
            if current:
                user = self.one("users", {"id": current["user_id"], "active": 1})
                if user:
                    row = {**fields(user, ("id", "username", "name", "role")),
                           **fields(current, ("last_seen", "timeout"))}
        elif op == "session_remove":
            return self.delete("sessions", {"token": p[0]})
        elif op == "user_sessions_remove":
            return self.delete("sessions", {"user_id": p[0]})
        elif op == "session_touch":
            return self.update("sessions", {"token": p[1]}, {"last_seen": p[0]})
        elif op == "sessions_cleanup":
            return self.delete("sessions", {"$or": [{"token": p[0]},
                {"$expr": {"$lte": [{"$add": ["$last_seen", "$timeout"]}, p[1]]}}]})
        elif op == "session_add":
            self.insert("sessions", dict(zip(("token", "user_id", "last_seen", "timeout"), p)))
        elif op in {"user_by_id", "user_by_username", "active_admin"}:
            query = ({"role": "02", "active": 1} if op == "active_admin" else
                     {"id" if op == "user_by_id" else "username": p[0]})
            row = self.one("users", query)
        elif op in {"admin_add", "user_add"}:
            attrs = ("username", "name", "password", "role") if op == "admin_add" else ("username", "name", "role")
            identifier = self.numbered("users", {"active": 1, "failures": 0, "locked_until": 0,
                                                 "password": None, **dict(zip(attrs, p))})
            row = {"id": identifier}
        elif op in {"user_failures", "user_unlock", "user_password", "user_edit"}:
            changes = {
                "user_failures": ("failures", "locked_until"), "user_unlock": (),
                "user_password": ("password",), "user_edit": ("name", "role", "active"),
            }
            reset = {"failures": 0, "locked_until": 0} if op in {"user_unlock", "user_password"} else {}
            return self.update("users", {"id": p[-1]}, {**reset, **dict(zip(changes[op], p[:-1]))})
        elif op == "user_remove":
            return self.delete("users", {"id": p[0]})
        elif op == "users_list":
            contacts = {c["user_id"]: c["email"] for c in self.many("user_contacts", {})}
            return Result({**fields(user, ("id", "username", "name", "role", "active")),
                           "configured": bool(user["password"]), "email": contacts.get(user["id"])}
                          for user in self.many("users", {}, [("username", 1)]))
        elif op == "invitation_add":
            self.insert("invitations", dict(zip(("token", "user_id", "expires"), p)))
        elif op == "invitation_remove":
            return self.delete("invitations", {"user_id": p[0]})
        elif op == "invited_user":
            invite = self.one("invitations", {"token": p[0], "expires": {"$gt": p[1]}})
            if invite:
                user = self.one("users", {"id": invite["user_id"], "active": 1})
                row = fields(user, ("id", "username")) if user else None
        elif op == "contact_save":
            return self.update("user_contacts", {"user_id": p[0]}, {"email": p[1]}, upsert=True)
        elif op == "contact_remove":
            return self.delete("user_contacts", {"user_id": p[0]})
        elif op == "contact_get":
            row = self.one("user_contacts", {"user_id": p[0]})
        elif op == "catalog_page":
            return self.catalog_page(p)
        elif op == "catalog_source":
            source = self.one("catalog_sources", {"product_id": p[0]})
            product = self.one("products", {"id": p[0]}) if source else None
            if product:
                row = {"price_status": source["price_status"], **fields(product, ("presentation", "price_cents"))}
        elif op in {"product_by_id", "product_by_barcode", "product_by_sku"}:
            key = {"product_by_id": "id", "product_by_barcode": "barcode", "product_by_sku": "sku"}[op]
            row = self.one("products", {key: p[0]})
        elif op == "product_add":
            row = {"id": self.numbered("products", {"active": 1, **dict(zip(self.product_fields, p))})}
        elif op == "product_edit":
            return self.update("products", {"id": p[-1]}, dict(zip((*self.product_fields, "active"), p[:-1])))
        elif op == "price_internal":
            return self.update("catalog_sources", {"product_id": p[0]}, {"price_status": "Precio interno"})
        elif op == "active_products":
            return Result(fields(product, ("id", "sku")) for product in self.many("products", {"active": 1}))
        elif op == "initial_import":
            row = self.one("imports", {"id": 1})
        elif op == "import_add":
            self.insert("imports", {"id": 1, "digest": p[0], "row_count": p[1]})
        elif op == "lots_add":
            if p:
                self.db.lots.insert_many([
                    {**dict(zip(("product_id", "lot", "expiry", "location", "quantity"), values)), "reserved": 0}
                    for values in p
                ], session=self.session)
        elif op.startswith("inventory_"):
            return self.inventory(op, p)
        else:
            raise ValueError(f"Operación MongoDB desconocida: {op}")
        return Result([row] if row is not None else [])

    def catalog_page(self, p):
        include_inactive, name, sku, barcode, brand, species, offset = p
        query = {"$or": [{"name": like(name)}, {"sku": like(sku)}, {"barcode": like(barcode)}],
                 "brand": like(brand), "species": like(species)}
        if not include_inactive:
            query["active"] = 1
        rows = self.many("products", query, [("name", 1), ("id", 1)], limit=26, skip=offset)
        statuses = self.many("catalog_sources", {"product_id": {"$in": [row["id"] for row in rows]}})
        by_product = {row["product_id"]: row["price_status"] for row in statuses}
        return Result({**row, "price_status": by_product.get(row["id"])} for row in rows)

    def inventory(self, op, p):
        if op == "inventory_lots":
            ids, real = p[:-1], p[-1]
            query = {"product_id": {"$in": list(ids)}, **self.visible_lots(real)}
            rows = self.many("lots", query, [("product_id", 1), ("expiry", 1), ("lot", 1), ("location", 1)])
            return Result({**fields(row, ("product_id", "lot", "expiry", "location")),
                           "available": row["quantity"] - row["reserved"]} for row in rows)
        query = {"active": 1}
        if op == "inventory_by_barcode":
            query["barcode"] = p[0]
        elif op == "inventory_search":
            query["name"] = like(p[0])
        else:
            query["id"] = {"$in": self.db.lots.distinct(
                "product_id", self.visible_lots(p[0]), session=self.session)}
        rows = self.many("products", query, [("name", 1), ("id", 1)], limit=25)
        return Result(fields(row, self.inventory_fields) for row in rows)

    @staticmethod
    def visible_lots(real):
        return {"lot": {"$not": re.compile("^DEMO-IT-")}} if real else {}
