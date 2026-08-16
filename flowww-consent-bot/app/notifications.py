"""Envío de notificaciones por WhatsApp (Twilio) y correo (SMTP).

Si no hay credenciales configuradas en el .env, cada sender cae en modo
"simulado": no intenta conectarse a nada, solo registra en el log lo que
habría enviado. Así el flujo completo se puede probar en local sin cuentas
reales de Twilio o SMTP.
"""

import logging
import smtplib
from email.mime.text import MIMEText

from app import config

logger = logging.getLogger("flowww_consent_bot.notifications")


def send_whatsapp(to_phone: str, message: str) -> str:
    """Devuelve 'sent' o 'mock' según si se envió de verdad."""
    if not to_phone:
        return "skipped"

    if not (config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_WHATSAPP_FROM):
        logger.info("[MOCK WhatsApp] a %s: %s", to_phone, message)
        return "mock"

    from twilio.rest import Client

    client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    to = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
    client.messages.create(from_=config.TWILIO_WHATSAPP_FROM, to=to, body=message)
    return "sent"


def send_email(to_email: str, subject: str, body: str) -> str:
    if not to_email:
        return "skipped"

    if not config.SMTP_HOST:
        logger.info("[MOCK Email] a %s | %s: %s", to_email, subject, body)
        return "mock"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config.SMTP_FROM
    msg["To"] = to_email

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        if config.SMTP_USER:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_FROM, [to_email], msg.as_string())
    return "sent"


def notify_patient(patient, sign_url: str, channel: str) -> dict:
    message = (
        f"Hola {patient.full_name}, por favor firma tu consentimiento informado "
        f"antes de tu tratamiento aquí: {sign_url}\n"
        "El enlace es personal y expira en 7 días."
    )
    results = {}
    if channel in ("whatsapp", "both"):
        results["whatsapp"] = send_whatsapp(patient.phone, message)
    if channel in ("email", "both"):
        results["email"] = send_email(patient.email, "Consentimiento informado pendiente de firma", message)
    return results
