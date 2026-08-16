import base64
import hashlib
import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.config import SIGNED_PDF_DIR


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
