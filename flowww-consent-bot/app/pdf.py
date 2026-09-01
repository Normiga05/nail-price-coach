import base64
import hashlib
import io
import json
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.clinical_history_fields import DISEASES
from app.config import SIGNED_PDF_DIR

MARGIN = 20 * mm


def _wrap_text(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, font: str, size: int, leading: float) -> float:
    c.setFont(font, size)
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if c.stringWidth(candidate, font, size) > max_width and line:
                c.drawString(x, y, line)
                y -= leading
                line = word
            else:
                line = candidate
        c.drawString(x, y, line)
        y -= leading
    return y


def _ensure_space(c: canvas.Canvas, y: float, needed: float, height: float) -> float:
    if y - needed < MARGIN:
        c.showPage()
        return height - MARGIN
    return y


def build_consent_pdf(consent_request, patient, template) -> tuple[str, str]:
    """Genera el PDF firmado y devuelve (ruta_relativa, hash_sha256)."""
    filename = f"consentimiento_{consent_request.id}_{consent_request.token[:8]}.pdf"
    path = SIGNED_PDF_DIR / filename

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20 * mm
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Consentimiento Informado")
    y -= 10 * mm

    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"Tratamiento: {template.treatment_name}")
    y -= 6 * mm
    c.drawString(margin, y, f"Paciente: {patient.full_name}")
    y -= 6 * mm
    c.drawString(margin, y, f"Contacto: {patient.phone or '-'} / {patient.email or '-'}")
    y -= 10 * mm

    y = _wrap_text(c, template.body_text, margin, y, width - 2 * margin, "Helvetica", 10, 5 * mm)
    y -= 8 * mm

    c.setFont("Helvetica-Oblique", 10)
    y = _wrap_text(
        c,
        f'Declaro que he leído y entendido este consentimiento y lo firmo voluntariamente como "{consent_request.signer_name}".',
        margin,
        y,
        width - 2 * margin,
        "Helvetica-Oblique",
        10,
        5 * mm,
    )
    y -= 10 * mm

    if consent_request.signature_data:
        try:
            header, encoded = consent_request.signature_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            img = ImageReader(io.BytesIO(img_bytes))
            c.drawImage(img, margin, y - 30 * mm, width=60 * mm, height=30 * mm, preserveAspectRatio=True, mask="auto")
            y -= 32 * mm
        except Exception:
            pass

    c.setFont("Helvetica", 8)
    c.drawString(margin, margin, f"Firmado el {consent_request.signed_at.strftime('%Y-%m-%d %H:%M UTC')}")
    c.drawString(margin, margin - 4 * mm, f"IP: {consent_request.signer_ip or '-'} | Token: {consent_request.token}")

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    doc_hash = hashlib.sha256(pdf_bytes).hexdigest()

    with open(path, "wb") as f:
        f.write(pdf_bytes)

    return str(path.relative_to(SIGNED_PDF_DIR.parent.parent)), doc_hash


def build_clinical_history_pdf(history, patient) -> tuple[str, str]:
    """Genera el PDF de la historia clínica rellenada y devuelve (ruta_relativa, hash_sha256)."""
    filename = f"historia_clinica_{history.id}.pdf"
    path = SIGNED_PDF_DIR / filename
    answers = json.loads(history.answers_json or "{}")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - MARGIN

    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN, y, "Historia Clínica")
    y -= 10 * mm

    c.setFont("Helvetica", 11)
    c.drawString(MARGIN, y, f"Paciente: {patient.full_name}")
    y -= 8 * mm

    fields = [
        ("Apellidos", answers.get("apellidos")),
        ("Nombres", answers.get("nombres")),
        ("DNI/NIE/Pasaporte", answers.get("dni")),
        ("Fecha de nacimiento", answers.get("fecha_nacimiento")),
        ("Dirección", answers.get("direccion")),
        ("Código postal", answers.get("codigo_postal")),
        ("Localidad", answers.get("localidad")),
        ("Teléfono", answers.get("telefono")),
        ("", ""),
        ("Motivo de consulta", answers.get("motivo_consulta")),
        ("Tratamiento estético previo", f"{answers.get('tratamiento_previo')} — {answers.get('tratamiento_previo_cuales') or '-'}"),
        ("Cirugía previa", f"{answers.get('cirugia_previa')} — {answers.get('cirugia_previa_detalle') or '-'}"),
        ("¿Puede estar embarazada?", answers.get("embarazada")),
        ("¿Amamantando?", answers.get("amamantando")),
        ("Alergias", f"{answers.get('alergias')} — {answers.get('alergias_detalle') or '-'}"),
        ("Enfermedad importante", f"{answers.get('enfermedad_importante')} — {answers.get('enfermedad_importante_detalle') or '-'}"),
        ("Medicación habitual", answers.get("medicacion_habitual") or "-"),
    ]

    for label, value in fields:
        if not label:
            y -= 3 * mm
            continue
        y = _ensure_space(c, y, 6 * mm, height)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, f"{label}:")
        y = _wrap_text(c, str(value or "-"), MARGIN + 55 * mm, y, width - MARGIN - (MARGIN + 55 * mm), "Helvetica", 10, 5 * mm)

    y = _ensure_space(c, y, 10 * mm, height)
    y -= 4 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Condiciones/enfermedades:")
    y -= 6 * mm

    disease_answers = answers.get("diseases", {})
    for key, label in DISEASES:
        y = _ensure_space(c, y, 5 * mm, height)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN, y, f"{label}: {disease_answers.get(key, 'no')}")
        y -= 5 * mm

    y = _ensure_space(c, y, 16 * mm, height)
    y -= 4 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Hábitos:")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, y, f"Alcohol: {answers.get('alcohol')} — {answers.get('alcohol_cuantas') or '-'}")
    y -= 5 * mm
    c.drawString(MARGIN, y, f"Fuma: {answers.get('fuma')} — {answers.get('fuma_cuantos') or '-'}")
    y -= 8 * mm

    if answers.get("notas_adicionales"):
        y = _ensure_space(c, y, 10 * mm, height)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, "Notas adicionales:")
        y -= 5 * mm
        y = _wrap_text(c, answers["notas_adicionales"], MARGIN, y, width - 2 * MARGIN, "Helvetica", 10, 5 * mm)

    y = _ensure_space(c, y, 40 * mm, height)
    y -= 8 * mm
    c.setFont("Helvetica-Oblique", 10)
    y = _wrap_text(
        c,
        f'Declaro que la información anterior es veraz y la firmo voluntariamente como "{history.signer_name}".',
        MARGIN,
        y,
        width - 2 * MARGIN,
        "Helvetica-Oblique",
        10,
        5 * mm,
    )
    y -= 10 * mm

    if history.signature_data:
        try:
            _header, encoded = history.signature_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            img = ImageReader(io.BytesIO(img_bytes))
            c.drawImage(img, MARGIN, y - 30 * mm, width=60 * mm, height=30 * mm, preserveAspectRatio=True, mask="auto")
            y -= 32 * mm
        except Exception:
            pass

    c.setFont("Helvetica", 8)
    c.drawString(MARGIN, MARGIN, f"Firmado el {history.submitted_at.strftime('%Y-%m-%d %H:%M UTC')}")
    c.drawString(MARGIN, MARGIN - 4 * mm, f"IP: {history.signer_ip or '-'}")

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    doc_hash = hashlib.sha256(pdf_bytes).hexdigest()

    with open(path, "wb") as f:
        f.write(pdf_bytes)

    return str(path.relative_to(SIGNED_PDF_DIR.parent.parent)), doc_hash
