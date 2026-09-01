"""Receptor de eventos externos (flowww, o un puente vía Zapier/Make/correo).

No sabemos todavía la forma exacta que tendrá el payload real de flowww (su
API sigue sin confirmar), así que este endpoint define un formato genérico y
documentado que cualquier integrador (flowww directo, Zapier, Make, o un
lector de correos de confirmación) puede rellenar. El día que se confirme el
formato real de flowww, solo hay que ajustar el parseo de `payload`, la
lógica de negocio (crear paciente, disparar consentimiento, programar
recordatorio) ya queda lista.

Payload esperado:
{
  "event": "appointment.created",      # o "treatment.completed"
  "external_id": "flowww-cita-123",     # id de la cita en el sistema de origen, evita duplicados
  "patient": {
    "full_name": "Maria Perez",
    "phone": "+34600111222",
    "email": "maria@example.com"
  },
  "treatment_names": ["Depilación láser", "Peeling químico"],  # 1 o más, deben coincidir con nombres de ConsentTemplate
  "appointment_at": "2026-08-20T10:00:00",
  "channel": "both"                       # opcional: whatsapp | email | both
}

Si la cita trae varios tratamientos, se manda UN SOLO enlace (ConsentPackage)
que agrupa todos los documentos pendientes, para que la paciente los firme
en una sola sesión en vez de recibir un mensaje por cada tratamiento.
"""

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config, notifications
from app.database import SessionLocal
from app.models import Appointment, ClinicalHistory, ConsentPackage, ConsentRequest, ConsentTemplate, Patient

router = APIRouter()


class PatientPayload(BaseModel):
    full_name: str
    phone: str | None = None
    email: str | None = None


class FlowwwEventPayload(BaseModel):
    event: str
    external_id: str
    patient: PatientPayload
    treatment_names: list[str]
    appointment_at: datetime | None = None
    channel: str = "both"


def _get_or_create_patient(db: Session, data: PatientPayload) -> Patient:
    patient = None
    if data.phone:
        patient = db.query(Patient).filter(Patient.phone == data.phone).first()
    if not patient and data.email:
        patient = db.query(Patient).filter(Patient.email == data.email).first()
    if not patient:
        patient = Patient(full_name=data.full_name, phone=data.phone, email=data.email)
        db.add(patient)
        db.flush()
    return patient


def _has_active_consent(db: Session, patient_id: int, template_id: int) -> bool:
    return (
        db.query(ConsentRequest)
        .filter(ConsentRequest.patient_id == patient_id, ConsentRequest.template_id == template_id)
        .filter(ConsentRequest.status != "expired")
        .first()
        is not None
    )


def process_flowww_event(db: Session, payload: FlowwwEventPayload) -> dict:
    """Lógica de negocio compartida: la usa el webhook HTTP y el lector de correo."""
    patient = _get_or_create_patient(db, payload.patient)

    appointment_result = "skipped"
    if payload.appointment_at:
        existing = db.query(Appointment).filter(Appointment.external_id == payload.external_id).first()
        if not existing:
            db.add(
                Appointment(
                    patient_id=patient.id,
                    treatment_name=", ".join(payload.treatment_names),
                    appointment_at=payload.appointment_at,
                    external_id=payload.external_id,
                    source="webhook",
                )
            )
            appointment_result = "created"
        else:
            appointment_result = "already_existed"

    matched_templates = []
    unmatched_names = []
    for name in payload.treatment_names:
        template = (
            db.query(ConsentTemplate)
            .filter(ConsentTemplate.treatment_name == name, ConsentTemplate.is_general.is_(False))
            .first()
        )
        if template:
            matched_templates.append(template)
        else:
            unmatched_names.append(name)

    general_templates = db.query(ConsentTemplate).filter(ConsentTemplate.is_general.is_(True)).all()
    pending_templates = [
        t for t in (general_templates + matched_templates) if not _has_active_consent(db, patient.id, t.id)
    ]
    needs_clinical_history = (
        db.query(ClinicalHistory).filter(ClinicalHistory.patient_id == patient.id).first() is None
    )

    if not pending_templates and not needs_clinical_history:
        consent_result = "already_sent"
    elif not payload.patient.phone and not payload.patient.email:
        consent_result = "no_contact_info"
    else:
        package = ConsentPackage(patient_id=patient.id, channel=payload.channel)
        db.add(package)
        db.flush()
        for template in pending_templates:
            db.add(
                ConsentRequest(
                    patient_id=patient.id,
                    template_id=template.id,
                    channel=payload.channel,
                    package_id=package.id,
                )
            )
        if needs_clinical_history:
            db.add(ClinicalHistory(patient_id=patient.id, package_id=package.id))
        db.commit()
        db.refresh(package)

        sign_url = f"{config.BASE_URL}/sign/{package.token}"
        notifications.notify_patient(patient, sign_url, payload.channel)

        package.status = "sent"
        package.sent_at = datetime.utcnow()
        parts = []
        if pending_templates:
            parts.append(f"{len(pending_templates)} documento(s)")
        if needs_clinical_history:
            parts.append("historia clínica")
        consent_result = "sent (" + " + ".join(parts) + ")"

    db.commit()
    return {
        "patient_id": patient.id,
        "appointment": appointment_result,
        "consent": consent_result,
        "unmatched_treatments": unmatched_names,
    }


@router.post("/webhooks/flowww")
def receive_flowww_event(payload: FlowwwEventPayload, x_webhook_secret: str = Header(default="")):
    if not config.WEBHOOK_SECRET or x_webhook_secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Secreto de webhook inválido")

    db = SessionLocal()
    try:
        return process_flowww_event(db, payload)
    finally:
        db.close()
