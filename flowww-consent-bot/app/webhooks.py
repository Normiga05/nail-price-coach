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
  "treatment_name": "Depilación láser",  # debe coincidir con el nombre de un ConsentTemplate
  "appointment_at": "2026-08-20T10:00:00",
  "channel": "both"                       # opcional: whatsapp | email | both
}
"""

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import config, notifications
from app.database import SessionLocal
from app.models import Appointment, ConsentRequest, ConsentTemplate, Patient

router = APIRouter()


class PatientPayload(BaseModel):
    full_name: str
    phone: str | None = None
    email: str | None = None


class FlowwwEventPayload(BaseModel):
    event: str
    external_id: str
    patient: PatientPayload
    treatment_name: str
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


@router.post("/webhooks/flowww")
def receive_flowww_event(payload: FlowwwEventPayload, x_webhook_secret: str = Header(default="")):
    if not config.WEBHOOK_SECRET or x_webhook_secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Secreto de webhook inválido")

    db = SessionLocal()
    try:
        patient = _get_or_create_patient(db, payload.patient)

        appointment_result = "skipped"
        if payload.appointment_at:
            existing = db.query(Appointment).filter(Appointment.external_id == payload.external_id).first()
            if not existing:
                db.add(
                    Appointment(
                        patient_id=patient.id,
                        treatment_name=payload.treatment_name,
                        appointment_at=payload.appointment_at,
                        external_id=payload.external_id,
                        source="webhook",
                    )
                )
                appointment_result = "created"
            else:
                appointment_result = "already_existed"

        template = db.query(ConsentTemplate).filter(ConsentTemplate.treatment_name == payload.treatment_name).first()
        consent_result = "no_matching_template"
        if template:
            already_sent = (
                db.query(ConsentRequest)
                .filter(ConsentRequest.patient_id == patient.id, ConsentRequest.template_id == template.id)
                .filter(ConsentRequest.status != "expired")
                .first()
            )
            if already_sent:
                consent_result = "already_sent"
            else:
                consent_request = ConsentRequest(patient_id=patient.id, template_id=template.id, channel=payload.channel)
                db.add(consent_request)
                db.commit()
                db.refresh(consent_request)

                sign_url = f"{config.BASE_URL}/sign/{consent_request.token}"
                notifications.notify_patient(patient, sign_url, payload.channel)

                consent_request.status = "sent"
                consent_request.sent_at = datetime.utcnow()
                consent_result = "sent"

        db.commit()
        return {"patient_id": patient.id, "appointment": appointment_result, "consent": consent_result}
    finally:
        db.close()
