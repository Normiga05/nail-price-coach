from datetime import datetime

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import config, notifications, pdf
from app.auth import require_admin
from app.database import Base, SessionLocal, engine, get_db
from app.models import ConsentPackage, ConsentRequest, ConsentTemplate, Patient
from app.scheduler import start_scheduler
from app.webhooks import router as webhooks_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="flowww Consent Bot")
app.include_router(webhooks_router)
templates = Jinja2Templates(directory=str(config.BASE_DIR / "app" / "templates"))
app.mount("/static", StaticFiles(directory=str(config.BASE_DIR / "app" / "static")), name="static")

SEED_TEMPLATES = [
    (
        "Depilación láser",
        "PLACEHOLDER - Este texto debe ser sustituido por el consentimiento informado "
        "real revisado por el equipo médico/legal de la clínica.\n\n"
        "Declaro haber sido informada sobre el procedimiento de depilación láser, "
        "sus beneficios esperados, los riesgos (irritación, quemaduras, cambios de "
        "pigmentación, entre otros) y las alternativas disponibles. He podido resolver "
        "mis dudas con el profesional y acepto someterme al tratamiento de forma voluntaria.",
    ),
    (
        "Peeling químico",
        "PLACEHOLDER - Este texto debe ser sustituido por el consentimiento informado "
        "real revisado por el equipo médico/legal de la clínica.\n\n"
        "Declaro haber sido informada sobre el procedimiento de peeling químico, "
        "sus beneficios esperados, los riesgos (enrojecimiento, descamación, "
        "hiperpigmentación, entre otros) y las alternativas disponibles. He podido "
        "resolver mis dudas con el profesional y acepto someterme al tratamiento de "
        "forma voluntaria.",
    ),
]


@app.on_event("startup")
def seed_templates():
    db = SessionLocal()
    try:
        if db.query(ConsentTemplate).count() == 0:
            for name, text in SEED_TEMPLATES:
                db.add(ConsentTemplate(treatment_name=name, body_text=text))
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def launch_reminder_scheduler():
    app.state.scheduler = start_scheduler()


@app.on_event("shutdown")
def stop_reminder_scheduler():
    app.state.scheduler.shutdown(wait=False)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return RedirectResponse("/admin")


@app.get("/admin")
def admin_list(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    requests_ = db.query(ConsentRequest).order_by(ConsentRequest.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin_list.html", {"requests": requests_})


@app.get("/admin/new")
def admin_new_form(request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    template_options = db.query(ConsentTemplate).all()
    return templates.TemplateResponse(request, "admin_new.html", {"templates": template_options})


@app.post("/admin/new")
def admin_new_submit(
    full_name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    template_id: int = Form(...),
    channel: str = Form("both"),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    patient = Patient(full_name=full_name, phone=phone or None, email=email or None)
    db.add(patient)
    db.flush()

    consent_request = ConsentRequest(patient_id=patient.id, template_id=template_id, channel=channel)
    db.add(consent_request)
    db.commit()
    db.refresh(consent_request)

    sign_url = f"{config.BASE_URL}/sign/{consent_request.token}"
    notifications.notify_patient(patient, sign_url, channel)

    consent_request.status = "sent"
    consent_request.sent_at = datetime.utcnow()
    db.commit()

    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/download/{request_id}")
def admin_download(request_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    consent_request = db.query(ConsentRequest).get(request_id)
    if not consent_request or not consent_request.pdf_path:
        return RedirectResponse("/admin")
    return FileResponse(config.BASE_DIR / consent_request.pdf_path, filename=f"consentimiento_{request_id}.pdf")


@app.get("/admin/templates")
def templates_list(
    request: Request, error: str = "", db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    template_options = db.query(ConsentTemplate).order_by(ConsentTemplate.treatment_name).all()
    error_message = "No se puede borrar: ya tiene consentimientos enviados con esta plantilla." if error == "en_uso" else None
    return templates.TemplateResponse(
        request, "templates_list.html", {"templates": template_options, "error_message": error_message}
    )


@app.get("/admin/templates/new")
def template_new_form(request: Request, _: str = Depends(require_admin)):
    return templates.TemplateResponse(
        request, "template_form.html", {"template": None, "form_action": "/admin/templates/new"}
    )


@app.post("/admin/templates/new")
def template_new_submit(
    treatment_name: str = Form(...),
    body_text: str = Form(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    db.add(ConsentTemplate(treatment_name=treatment_name.strip(), body_text=body_text))
    db.commit()
    return RedirectResponse("/admin/templates", status_code=303)


@app.get("/admin/templates/{template_id}/edit")
def template_edit_form(template_id: int, request: Request, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    template = db.query(ConsentTemplate).get(template_id)
    if not template:
        return RedirectResponse("/admin/templates")
    return templates.TemplateResponse(
        request, "template_form.html", {"template": template, "form_action": f"/admin/templates/{template_id}/edit"}
    )


@app.post("/admin/templates/{template_id}/edit")
def template_edit_submit(
    template_id: int,
    treatment_name: str = Form(...),
    body_text: str = Form(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    template = db.query(ConsentTemplate).get(template_id)
    if template:
        template.treatment_name = treatment_name.strip()
        template.body_text = body_text
        db.commit()
    return RedirectResponse("/admin/templates", status_code=303)


@app.post("/admin/templates/{template_id}/delete")
def template_delete(template_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    template = db.query(ConsentTemplate).get(template_id)
    if template:
        in_use = db.query(ConsentRequest).filter(ConsentRequest.template_id == template_id).first() is not None
        if not in_use:
            db.delete(template)
            db.commit()
        else:
            return RedirectResponse("/admin/templates?error=en_uso", status_code=303)
    return RedirectResponse("/admin/templates", status_code=303)


def _save_signature(db: Session, consent_request: ConsentRequest, request: Request, signer_name: str, signature_data: str):
    consent_request.signer_name = signer_name
    consent_request.signature_data = signature_data
    consent_request.signer_ip = request.client.host if request.client else None
    consent_request.signer_user_agent = request.headers.get("user-agent", "")
    consent_request.signed_at = datetime.utcnow()
    consent_request.status = "signed"
    db.commit()
    db.refresh(consent_request)

    pdf_path, doc_hash = pdf.build_consent_pdf(consent_request, consent_request.patient, consent_request.template)
    consent_request.pdf_path = pdf_path
    consent_request.doc_hash = doc_hash
    db.commit()


@app.get("/sign/{token}")
def sign_form(token: str, request: Request, db: Session = Depends(get_db)):
    package = db.query(ConsentPackage).filter(ConsentPackage.token == token).first()
    if package:
        if package.expires_at and package.expires_at < datetime.utcnow() and package.status != "signed":
            package.status = "expired"
            db.commit()
            return templates.TemplateResponse(
                request, "expired.html", {"message": "Este enlace ha expirado. Pide a la clínica que te envíe uno nuevo."}
            )
        if all(item.status == "signed" for item in package.items):
            if package.status != "signed":
                package.status = "signed"
                package.completed_at = datetime.utcnow()
                db.commit()
            return templates.TemplateResponse(request, "package_confirmation.html", {"package": package})
        return templates.TemplateResponse(request, "package_overview.html", {"package": package, "items": package.items})

    consent_request = db.query(ConsentRequest).filter(ConsentRequest.token == token).first()
    if not consent_request:
        return templates.TemplateResponse(request, "expired.html", {"message": "Este enlace no existe."})
    if consent_request.status == "signed":
        return templates.TemplateResponse(request, "signed_confirmation.html", {"consent": consent_request})
    if consent_request.expires_at and consent_request.expires_at < datetime.utcnow():
        consent_request.status = "expired"
        db.commit()
        return templates.TemplateResponse(
            request, "expired.html", {"message": "Este enlace ha expirado. Pide a la clínica que te envíe uno nuevo."}
        )
    return templates.TemplateResponse(
        request, "sign.html", {"consent": consent_request, "sign_action_url": f"/sign/{token}", "progress_label": None}
    )


@app.post("/sign/{token}")
def sign_submit(
    token: str,
    request: Request,
    signer_name: str = Form(...),
    signature_data: str = Form(...),
    db: Session = Depends(get_db),
):
    consent_request = db.query(ConsentRequest).filter(ConsentRequest.token == token).first()
    if not consent_request or consent_request.status == "signed":
        return RedirectResponse(f"/sign/{token}")

    _save_signature(db, consent_request, request, signer_name, signature_data)
    return templates.TemplateResponse(request, "signed_confirmation.html", {"consent": consent_request})


@app.get("/sign/{token}/item/{item_id}")
def sign_package_item_form(token: str, item_id: int, request: Request, db: Session = Depends(get_db)):
    package = db.query(ConsentPackage).filter(ConsentPackage.token == token).first()
    if not package:
        return templates.TemplateResponse(request, "expired.html", {"message": "Este enlace no existe."})
    item = next((i for i in package.items if i.id == item_id), None)
    if not item:
        return templates.TemplateResponse(request, "expired.html", {"message": "Este documento no existe."})
    if item.status == "signed":
        return RedirectResponse(f"/sign/{token}")

    index = package.items.index(item) + 1
    progress_label = f"Documento {index} de {len(package.items)}"
    return templates.TemplateResponse(
        request,
        "sign.html",
        {"consent": item, "sign_action_url": f"/sign/{token}/item/{item_id}", "progress_label": progress_label},
    )


@app.post("/sign/{token}/item/{item_id}")
def sign_package_item_submit(
    token: str,
    item_id: int,
    request: Request,
    signer_name: str = Form(...),
    signature_data: str = Form(...),
    db: Session = Depends(get_db),
):
    package = db.query(ConsentPackage).filter(ConsentPackage.token == token).first()
    if not package:
        return RedirectResponse(f"/sign/{token}")
    item = next((i for i in package.items if i.id == item_id), None)
    if not item or item.status == "signed":
        return RedirectResponse(f"/sign/{token}")

    _save_signature(db, item, request, signer_name, signature_data)
    return RedirectResponse(f"/sign/{token}")
