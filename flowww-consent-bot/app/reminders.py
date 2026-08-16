"""Recordatorios automáticos de cita.

Revisa periódicamente las citas guardadas (creadas por el webhook de
flowww/Zapier, o manualmente) y manda un recordatorio por WhatsApp/correo
cuando falta REMINDER_LEAD_HOURS horas o menos para la cita, una sola vez.
"""

import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app import config, notifications
from app.database import SessionLocal
from app.models import Appointment

logger = logging.getLogger("flowww_consent_bot.reminders")

_GRACE_PERIOD = timedelta(hours=6)  # citas ya pasadas por más de esto ya no se recuerdan


def check_and_send_reminders() -> int:
    db = SessionLocal()
    sent = 0
    try:
        now = datetime.utcnow()
        window_end = now + timedelta(hours=config.REMINDER_LEAD_HOURS)

        due = (
            db.query(Appointment)
            .filter(Appointment.reminder_sent == 0)
            .filter(Appointment.appointment_at <= window_end)
            .filter(Appointment.appointment_at >= now - _GRACE_PERIOD)
            .all()
        )

        for appointment in due:
            patient = appointment.patient
            message = (
                f"Hola {patient.full_name}, te recordamos tu cita de "
                f"{appointment.treatment_name} el "
                f"{appointment.appointment_at.strftime('%d/%m/%Y a las %H:%M')}."
            )
            notifications.send_whatsapp(patient.phone, message)
            notifications.send_email(patient.email, "Recordatorio de tu cita", message)
            appointment.reminder_sent = 1
            sent += 1

        # Citas vencidas hace mucho sin recordatorio: se marcan como enviadas
        # igual para no reintentarlas indefinidamente, sin mandar nada.
        stale = (
            db.query(Appointment)
            .filter(Appointment.reminder_sent == 0)
            .filter(Appointment.appointment_at < now - _GRACE_PERIOD)
            .all()
        )
        for appointment in stale:
            appointment.reminder_sent = 1

        db.commit()
    finally:
        db.close()

    if sent:
        logger.info("Recordatorios enviados: %d", sent)
    return sent


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(check_and_send_reminders, "interval", minutes=5, id="appointment_reminders")
    scheduler.start()
    return scheduler
