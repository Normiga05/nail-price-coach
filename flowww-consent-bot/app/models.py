import secrets
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
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
    is_general = Column(Boolean, default=False)  # se manda a toda paciente nueva, sin importar el tratamiento
    created_at = Column(DateTime, default=datetime.utcnow)

    consent_requests = relationship("ConsentRequest", back_populates="template")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    treatment_name = Column(String(200), nullable=False)
    appointment_at = Column(DateTime, nullable=False)
    external_id = Column(String(120), unique=True, nullable=True)  # id de la cita en flowww, evita duplicados
    source = Column(String(20), default="webhook")  # webhook | manual

    reminder_sent = Column(Integer, default=0)  # 0/1 como bandera simple
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")


class ConsentPackage(Base):
    """Agrupa varios ConsentRequest (uno por tratamiento) detrás de un solo
    enlace, para cuando una paciente tiene varios tratamientos en la misma
    cita y firma todo en una sola sesión."""

    __tablename__ = "consent_packages"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, index=True, default=generate_token)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    channel = Column(String(20), default="both")
    status = Column(String(20), default="pending")  # pending | sent | signed | expired

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=default_expiry)

    patient = relationship("Patient")
    items = relationship("ConsentRequest", back_populates="package", order_by="ConsentRequest.id")
    clinical_history = relationship("ClinicalHistory", back_populates="package", uselist=False)


class ConsentRequest(Base):
    __tablename__ = "consent_requests"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, index=True, default=generate_token)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("consent_templates.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("consent_packages.id"), nullable=True)

    channel = Column(String(20), default="both")  # whatsapp | email | both
    status = Column(String(20), default="pending")  # pending | sent | signed | expired

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=default_expiry)

    signer_name = Column(String(200), nullable=True)
    signature_data = Column(Text, nullable=True)  # base64 PNG de la firma dibujada
    signer_ip = Column(String(60), nullable=True)
    signer_user_agent = Column(String(300), nullable=True)
    doc_hash = Column(String(80), nullable=True)
    pdf_path = Column(String(300), nullable=True)

    patient = relationship("Patient", back_populates="consent_requests")
    template = relationship("ConsentTemplate", back_populates="consent_requests")
    package = relationship("ConsentPackage", back_populates="items")


class ClinicalHistory(Base):
    """Formulario de historia clínica (cuestionario médico), distinto de un
    consentimiento: no es "leer y firmar" sino rellenar datos + un
    cuestionario de sí/no y texto libre, y al final firmar. Se manda una
    sola vez por paciente, junto con su primer tratamiento."""

    __tablename__ = "clinical_histories"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("consent_packages.id"), nullable=True)

    status = Column(String(20), default="pending")  # pending | signed

    answers_json = Column(Text, nullable=True)  # respuestas del cuestionario, como JSON

    signer_name = Column(String(200), nullable=True)
    signature_data = Column(Text, nullable=True)
    signer_ip = Column(String(60), nullable=True)
    signer_user_agent = Column(String(300), nullable=True)
    doc_hash = Column(String(80), nullable=True)
    pdf_path = Column(String(300), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    patient = relationship("Patient")
    package = relationship("ConsentPackage", back_populates="clinical_history")
