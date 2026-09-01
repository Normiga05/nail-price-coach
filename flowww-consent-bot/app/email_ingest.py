"""Lee una bandeja de correo por IMAP buscando los correos reales que manda
flowww ("Notificaciones FLOWww <noreply@flowww.com>", asunto "Confirmación
de reserva") y los traduce al mismo evento que entiende /webhooks/flowww,
disparando el consentimiento automáticamente.

Basado en un correo real de ejemplo (datos anonimizados aquí):

    Nombre del paciente:  Maria Perez
    Código del paciente:  1234
    Clínica:              Clínica Ejemplo S.L
    Dirección:            Calle Ejemplo 1

    Fecha       Hora Inicio   Hora Fin   Tratamientos
    17/09/2026  11:30         12:00      Toxina Botulínica 3 zonas

Ese correo NO trae teléfono de la paciente, así que por esta vía solo se
puede automatizar el envío por correo, no por WhatsApp, a menos que se
cruce el "código de paciente" con una lista de contactos aparte.

flowww manda este correo directo a quien esté registrado como email de la
paciente, no a la clínica — así que la clínica no puede simplemente
"reenviarlo" (nunca les llega a ellos). Para que nos llegue una copia hace
falta que flowww tenga una opción de configuración de "copia interna" que
apunte a la bandeja que se conecta aquí (ver README).
"""

import email
import hashlib
import imaplib
import logging
import re
from datetime import datetime
from email.header import decode_header

from bs4 import BeautifulSoup

from app import config
from app.database import SessionLocal
from app.webhooks import FlowwwEventPayload, PatientPayload, process_flowww_event

logger = logging.getLogger("flowww_consent_bot.email_ingest")

FIELD_PATTERNS = {
    "full_name": re.compile(r"Nombre del paciente:\s*(.+)"),
    "patient_code": re.compile(r"C[oó]digo del paciente:\s*(\S+)"),
}
ROW_PATTERN = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s*\n?\s*(\d{2}:\d{2})\s*\n?\s*(\d{2}:\d{2})\s*\n?\s*(.+)"
)


def _decode(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    return "".join(
        part.decode(enc or "utf-8", errors="ignore") if isinstance(part, bytes) else part for part, enc in parts
    )


def _extract_text(msg: email.message.Message) -> str:
    html_body = None
    text_body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html" and html_body is None:
                html_body = part.get_payload(decode=True)
            elif content_type == "text/plain" and text_body is None:
                text_body = part.get_payload(decode=True)
    else:
        if msg.get_content_type() == "text/html":
            html_body = msg.get_payload(decode=True)
        else:
            text_body = msg.get_payload(decode=True)

    if html_body:
        soup = BeautifulSoup(html_body, "html.parser")
        return soup.get_text(separator="\n")
    if text_body:
        return text_body.decode("utf-8", errors="ignore")
    return ""


def parse_confirmation_email(msg: email.message.Message) -> dict | None:
    text = _extract_text(msg)
    if not text.strip():
        return None

    full_name_match = FIELD_PATTERNS["full_name"].search(text)
    code_match = FIELD_PATTERNS["patient_code"].search(text)
    row_match = ROW_PATTERN.search(text)

    if not (full_name_match and code_match and row_match):
        logger.warning("No se pudo extraer la info esperada del correo, se ignora.")
        return None

    full_name = full_name_match.group(1).strip()
    patient_code = code_match.group(1).strip()
    fecha, hora_inicio, _hora_fin, treatment_name = row_match.groups()
    treatment_name = treatment_name.strip().splitlines()[0].strip()

    appointment_at = datetime.strptime(f"{fecha} {hora_inicio}", "%d/%m/%Y %H:%M")

    # flowww manda este correo directo al email de la paciente; si a esta
    # bandeja le llega directo (porque así lo configuró la clínica) el
    # "Para:" del correo ES el correo real de la paciente.
    patient_email = email.utils.parseaddr(msg.get("To", ""))[1] or None

    external_id = "email-" + hashlib.sha256(f"{patient_code}-{fecha}-{hora_inicio}".encode()).hexdigest()[:16]

    return {
        "external_id": external_id,
        "full_name": full_name,
        "patient_email": patient_email,
        "treatment_name": treatment_name,
        "appointment_at": appointment_at,
    }


def check_flowww_inbox() -> int:
    if not (config.EMAIL_IMAP_HOST and config.EMAIL_IMAP_USER and config.EMAIL_IMAP_PASSWORD):
        return 0

    processed = 0
    conn = imaplib.IMAP4_SSL(config.EMAIL_IMAP_HOST, config.EMAIL_IMAP_PORT)
    try:
        conn.login(config.EMAIL_IMAP_USER, config.EMAIL_IMAP_PASSWORD)
        conn.select(config.EMAIL_IMAP_FOLDER)

        status_, data = conn.search(None, "UNSEEN", "FROM", f'"{config.FLOWWW_SENDER_EMAIL}"')
        if status_ != "OK":
            return 0

        db = SessionLocal()
        try:
            for msg_id in data[0].split():
                status_, msg_data = conn.fetch(msg_id, "(RFC822)")
                if status_ != "OK" or not msg_data or not msg_data[0]:
                    continue

                msg = email.message_from_bytes(msg_data[0][1])
                subject = _decode(msg.get("Subject"))
                if "reserva" not in subject.lower():
                    conn.store(msg_id, "+FLAGS", "\\Seen")
                    continue

                parsed = parse_confirmation_email(msg)
                conn.store(msg_id, "+FLAGS", "\\Seen")
                if not parsed:
                    continue

                payload = FlowwwEventPayload(
                    event="appointment.created",
                    external_id=parsed["external_id"],
                    patient=PatientPayload(
                        full_name=parsed["full_name"],
                        phone=None,
                        email=parsed["patient_email"],
                    ),
                    treatment_name=parsed["treatment_name"],
                    appointment_at=parsed["appointment_at"],
                    channel="email",
                )
                result = process_flowww_event(db, payload)
                logger.info("Correo de flowww procesado: %s", result)
                processed += 1
        finally:
            db.close()
    finally:
        conn.logout()

    return processed
