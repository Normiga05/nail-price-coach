"""Arranca el proceso en segundo plano que corre cada 5 minutos: revisa la
bandeja de correo por confirmaciones nuevas de flowww y manda los
recordatorios de cita que ya tocan.
"""

from apscheduler.schedulers.background import BackgroundScheduler

from app.email_ingest import check_flowww_inbox
from app.reminders import check_and_send_reminders


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(check_and_send_reminders, "interval", minutes=5, id="appointment_reminders")
    scheduler.add_job(check_flowww_inbox, "interval", minutes=5, id="flowww_email_ingest")
    scheduler.start()
    return scheduler
