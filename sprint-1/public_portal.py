"""Public contact requests and account recovery, using the existing durable store."""
import re
import secrets
import time
from datetime import datetime, timezone

from app import Problem, audit, digest, field, run_db, send_email, transaction
from commerce import all_records, find, save

CONTACT_FIELDS = ("phone", "email", "legal_name", "nit", "address", "hours")
INTERESTS = {"Avicultura", "Ganadería", "Porcicultura", "Más líneas"}
GENERIC_RECOVERY = "Si el usuario y el correo coinciden con una cuenta activa, recibirás un enlace para configurar tu contraseña. Revisa también la carpeta de correo no deseado."


def contact(db):
    values = find(db, "settings", "public-contact") or {}
    return {key: str(values.get(key, "+573207424661" if key == "phone" else "")) for key in CONTACT_FIELDS}


def validate_contact(data):
    result = {key: str(data.get(key, "")).strip()[:200] for key in CONTACT_FIELDS}
    result["phone"] = re.sub(r"[\s()\-]", "", result["phone"])
    if result["phone"] and not re.fullmatch(r"\+?[1-9][0-9]{8,14}", result["phone"]):
        raise Problem("Indica el teléfono con el código de país, por ejemplo +57 seguido del número.")
    if result["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", result["email"]):
        raise Problem("Revisa el correo de contacto.")
    return result


def allowance(db, ip, kind, maximum):
    key = kind + "-" + digest(ip)
    row = find(db, "public_limits", key) or {"id": key, "start": 0, "count": 0}
    if time.time() - row["start"] > 3600:
        row.update(start=int(time.time()), count=0)
    if row["count"] >= maximum:
        raise Problem("Has enviado varias solicitudes. Inténtalo dentro de una hora o comunícate por WhatsApp.", 429)
    row["count"] += 1
    save(db, "public_limits", row)


def submit_request(handler, db):
    data = handler.data()
    if data.get("website"):
        return handler.respond({"ok": True, "message": "Solicitud recibida."})
    name = field(data, "name", 100)
    email = field(data, "email", 200).lower()
    phone = field(data, "phone", 30)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise Problem("Escribe un correo válido para que podamos contactarte.")
    if not re.fullmatch(r"\+?[0-9 ()-]{7,30}", phone) or not 7 <= len(re.sub(r"\D", "", phone)) <= 15:
        raise Problem("Revisa el número de contacto.")
    if data.get("consent") is not True:
        raise Problem("Autoriza el contacto para enviar tu solicitud.")
    interest = field(data, "interest", 50)
    if interest not in INTERESTS:
        raise Problem("Selecciona tu línea de interés.")
    request_id = field(data, "request_id", 64)
    if not re.fullmatch(r"[a-fA-F0-9-]{32,36}", request_id):
        raise Problem("Vuelve a abrir el formulario e inténtalo nuevamente.")
    with transaction(db):
        existing = find(db, "account_requests", request_id)
        if existing:
            if existing["email"] != email:
                raise Problem("Vuelve a enviar la solicitud.", 409)
        else:
            allowance(db, handler.ip, "account", 8)
            save(db, "account_requests", {"id": request_id, "name": name, "email": email,
                "phone": phone, "farm": str(data.get("farm", "")).strip()[:150], "interest": interest,
                "status": "PENDIENTE", "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "consent": True})
    return handler.respond({"ok": True, "message": "Tu solicitud quedó registrada. El equipo de Villali revisará tus datos para ayudarte con el acceso."})


def recover(handler, db):
    data = handler.data()
    username = field(data, "username", 80).lower()
    email = field(data, "email", 200).lower()
    token = secrets.token_urlsafe(32)
    user = None
    with transaction(db):
        allowance(db, handler.ip, "recovery", 8)
        row = run_db(db, "user_by_username", "SELECT * FROM users WHERE username=?", (username,)).fetchone()
        saved = run_db(db, "contact_get", "SELECT email FROM user_contacts WHERE user_id=?", (row["id"],)).fetchone() if row else None
        if row and row["active"] and saved and saved["email"].lower() == email:
            # Reuse the single-use activation flow; no password changes until the recipient redeems the link.
            run_db(db, "invitation_remove", "DELETE FROM invitations WHERE user_id=?", (row["id"],))
            run_db(db, "invitation_add", "INSERT INTO invitations VALUES(?,?,?)", (digest(token), row["id"], int(time.time()) + 1800))
            user = dict(row)
    if user:
        status = send_email(email, "Recupera tu acceso a Villali",
            "Configura tu contraseña con este enlace de un solo uso, válido por 30 minutos:\n" +
            handler.server.origin + "/entrar#invitar=" + token,
            "recovery-" + digest(token))
        audit(db, username, "RECUPERACION_SOLICITADA", handler.ip, status)
    return handler.respond({"ok": True, "message": GENERIC_RECOVERY})


def manage(handler, db, actor, method, kind):
    handler.require(db, actor, {"02"}, "/api/public-admin/" + kind)
    if method == "GET":
        if kind == "contact":
            return handler.respond(contact(db))
        return handler.respond(sorted(all_records(db, "account_requests"), key=lambda row: row["at"], reverse=True))
    if method != "POST":
        raise Problem("Método no permitido.", 405)
    data = handler.data()
    with transaction(db):
        current = run_db(db, "user_by_id", "SELECT * FROM users WHERE id=?", (actor["id"],)).fetchone()
        if not current or not current["active"] or current["role"] != "02":
            raise Problem("Inicia sesión de nuevo.", 401)
        if kind == "contact":
            result = save(db, "settings", {"id": "public-contact", **validate_contact(data)})
        else:
            result = find(db, "account_requests", data.get("id"))
            if not result:
                raise Problem("Solicitud no encontrada.", 404)
            if data.get("status") not in {"PENDIENTE", "CONTACTADO"}:
                raise Problem("Selecciona un estado válido.")
            result["status"] = data["status"]
            save(db, "account_requests", result)
        audit(db, actor["username"], "PORTADA_ACTUALIZADA", handler.ip, kind)
    return handler.respond({"ok": True})
