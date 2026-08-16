import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SIGNED_PDF_DIR = DATA_DIR / "signed"
DATA_DIR.mkdir(exist_ok=True)
SIGNED_PDF_DIR.mkdir(exist_ok=True)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'app.db'}")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "consentimientos@tuestetica.com")

ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# Secreto compartido para autenticar el webhook entrante (de flowww, Zapier, Make, etc.)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Con cuántas horas de antelación se manda el recordatorio de cita
REMINDER_LEAD_HOURS = int(os.getenv("REMINDER_LEAD_HOURS", "24"))
