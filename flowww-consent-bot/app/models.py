import secrets
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


def generate_token() -> str:
    return secrets.token_urlsafe(24)


def default_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=7)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(40))
    email = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    consent_requests = relationship("ConsentRequest", back_populates="patient")


class ConsentTemplate(Base):
    __tablename__ = "consent_templates"

    id = Column(Integer, primary_key=True)
    treatment_name = Column(String(200), nullable=False)
    body_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consent_requests = relationship("ConsentRequest", back_populates="template")


class ConsentRequest(Base):
    __tablename__ = "consent_requests"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, index=True, default=generate_token)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("consent_templates.id"), nullable=False)

    channel = Column(String(20), default="both")  # whatsapp | email | both
    status = Column(String(20), default="pending")  # pending | sent | signed | expired

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=default_expiry)

    signer_name = Column(String(200), nullable=True)
    signature_data = Column(Text, nullable=True)  # base64 PNG of the drawn signature
    signer_ip = Column(String(60), nullable=True)
    signer_user_agent = Column(String(300), nullable=True)
    doc_hash = Column(String(80), nullable=True)
    pdf_path = Column(String(300), nullable=True)

    patient = relationship("Patient", back_populates="consent_requests")
    template = relationship("ConsentTemplate", back_populates="consent_requests")
