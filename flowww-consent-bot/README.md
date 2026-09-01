# flowww Consent Bot

Bot para que las pacientes de una clínica estética firmen el consentimiento
informado de un tratamiento 100% online, sin papel, recibiendo el enlace de
firma por WhatsApp y/o correo.

Este proyecto es independiente de flowww. El staff puede crear un
consentimiento a mano en el panel, y además ya existe un webhook
(`/webhooks/flowww`) listo para recibir eventos automáticos de citas/
tratamientos en cuanto flowww (o un puente vía Zapier/Make) confirme cómo
entregar esos datos — ver "Automatización con flowww" más abajo.

## Gestión de plantillas (`/admin/templates`)

Cada tratamiento es solo una fila en la base de datos (nombre + texto
legal) — no hay límite ni trabajo extra por tener 10, 30 o 60 tratamientos
distintos. Desde `/admin/templates` el staff puede crear, editar y borrar
plantillas sin depender de que alguien toque el código. El nombre del
tratamiento debe coincidir exactamente con el que usa flowww para que el
envío automático (webhook/correo) lo reconozca. No se borra una plantilla
que ya tenga consentimientos enviados, para no romper el historial.

## Flujo

1. El staff entra a `/admin/new`, elige la paciente y el tratamiento (o llega
   automáticamente vía webhook/correo).
2. El bot genera un enlace único de firma y lo envía por WhatsApp (Twilio) y/o
   correo (SMTP).
3. La paciente abre el enlace, lee el consentimiento, escribe su nombre y
   firma con el dedo/ratón.
4. El bot genera un PDF firmado con la evidencia (IP, fecha/hora, hash del
   documento) y lo guarda. El staff lo ve y descarga desde `/admin`.

## Documentos generales vs. por tratamiento

No todos los documentos van atados a un tratamiento. Una `ConsentTemplate`
puede marcarse como **general** (`is_general`, casilla en `/admin/templates`)
— esos se mandan una sola vez a toda paciente nueva, sin importar qué
tratamiento tenga agendado (ej. Protección de Datos/LOPD). Ya viene
sembrado el texto real de Protección de Datos de la clínica.

Además existe la **Historia Clínica**, que no es un documento de "leer y
firmar" sino un formulario real (datos personales + cuestionario médico:
alergias, medicación, ~20 condiciones de salud, embarazo, hábitos, etc. —
ver `app/clinical_history_fields.py`). También se manda una sola vez por
paciente. Cuando llega un evento (webhook o correo) de una paciente que
todavía no tiene historia clínica ni ha firmado los documentos generales,
el bot los agrega automáticamente al mismo `ConsentPackage` que el
tratamiento — la paciente lo completa todo en una sola sesión la primera
vez; en visitas siguientes, solo le llega el consentimiento del tratamiento
nuevo.

El teléfono que la paciente escribe al rellenar la Historia Clínica se
guarda en su ficha automáticamente (si todavía no lo teníamos), para que
desde su siguiente cita el envío también pueda salir por WhatsApp y no
solo por correo.

## Importar pacientes existentes (`/admin/patients/import`)

Los correos de flowww solo traen el email de la paciente, no el teléfono
— así que la primera vez que una paciente pasa por el bot, el envío por
WhatsApp depende de que ya tengamos su teléfono guardado (si no, sale solo
por correo hasta que complete la Historia Clínica).

Para no depender de eso con las pacientes que la clínica ya tiene desde
antes, `/admin/patients/import` acepta un CSV con columnas
`nombre,telefono,email` y crea/actualiza sus fichas de una sola vez — así
desde la primera cita que pase por el bot, ya sale por WhatsApp también.
Hace *match* por email si lo trae (para coincidir con lo que manda
flowww), si no por teléfono.

## Arranque local

```bash
cd flowww-consent-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Abre `http://localhost:8000/admin`. Te pedirá usuario/contraseña: si no
pusiste `ADMIN_USER`/`ADMIN_PASSWORD` en el `.env`, revisa el log de arranque
del servidor, ahí se imprime una contraseña temporal generada al vuelo. El
panel `/admin` siempre requiere login porque ahí se ven datos de pacientes
(nombre, teléfono, correo); la página pública `/sign/{token}` que recibe la
paciente no lo necesita.

Sin credenciales de Twilio/SMTP en `.env`, el envío de WhatsApp y correo
corre en **modo simulado**: no se envía nada real, solo queda en el log del
servidor (`[MOCK WhatsApp]` / `[MOCK Email]`). Esto permite probar todo el
flujo (crear consentimiento → firmar → generar PDF) sin cuentas reales.

## Desplegarlo en una URL pública (Render)

Para que el enlace de firma funcione desde un WhatsApp o correo real (no
solo en local) hace falta una URL pública:

1. Crea una cuenta gratis en [render.com](https://render.com) y conecta este
   repo.
2. Render detecta `render.yaml` automáticamente (Blueprint). Al desplegar te
   pedirá rellenar las variables marcadas `sync: false` (`ADMIN_USER`,
   `ADMIN_PASSWORD`, credenciales de Twilio/SMTP si ya las tienes, y
   `BASE_URL` con la URL pública que Render te asigna).
3. El plan free de Render no tiene disco persistente, así que la base SQLite
   se reinicia en cada redeploy — bien para hacer una demo, no para
   producción real (ahí conviene Postgres, ver más abajo).

## Automatización con flowww (webhook + recordatorios)

Cuando se confirme el acceso a flowww (API/webhooks, o un puente vía
Zapier/Make/correo), no hace falta programar nada nuevo: ya existe
`POST /webhooks/flowww`, protegido con un secreto compartido
(`WEBHOOK_SECRET` en `.env`, se manda en el header `X-Webhook-Secret`).

Formato de payload esperado (ver `app/webhooks.py` para el detalle):

```json
{
  "event": "appointment.created",
  "external_id": "id-de-la-cita-en-flowww",
  "patient": { "full_name": "...", "phone": "+34...", "email": "..." },
  "treatment_names": ["Depilación láser", "Peeling químico"],
  "appointment_at": "2026-08-20T10:00:00",
  "channel": "both"
}
```

Al recibir un evento:
1. Busca o crea la paciente (por teléfono o correo, evita duplicados).
2. Guarda la cita (deduplicada por `external_id`).
3. Por cada nombre en `treatment_names` que coincida con una plantilla de
   consentimiento existente, agrupa todos los pendientes en **un solo
   enlace** (`ConsentPackage`) y lo manda automáticamente por WhatsApp/
   correo — sin que el staff tenga que hacer nada. Si la paciente tiene una
   sola cita con un solo tratamiento, el paquete tiene un solo documento;
   si tiene varios en la misma cita, los firma todos en la misma sesión
   ("Documento 1 de 3", etc.), sin recibir un mensaje distinto por cada uno.
4. Un job en segundo plano revisa cada 5 minutos las citas guardadas y manda
   un **recordatorio automático** (`REMINDER_LEAD_HOURS` en `.env`, 24h por
   defecto) antes de la hora de la cita, una sola vez por cita.

Si flowww no expone webhooks pero sí manda un correo de confirmación al
agendar/completar un tratamiento, la misma ruta sirve de destino para un
lector de correos automático (ej. vía Mailgun/SendGrid inbound routing) que
traduzca ese correo al formato de arriba — no requiere volver a tocar la
lógica de negocio, solo ese primer parseo.

## Lector de correo de flowww (`app/email_ingest.py`)

Ya está construido y probado contra un correo real de flowww (asunto
"Confirmación de reserva", remitente `noreply@flowww.com`): extrae nombre
de la paciente, código de paciente, tratamiento y fecha/hora, y dispara el
mismo flujo de arriba automáticamente.

**Aviso importante**: ese correo lo manda flowww directo al email
registrado de la paciente, no a la clínica — así que la clínica no puede
simplemente "reenviarlo" (nunca les llega a ellos). Para que el bot reciba
una copia de verdad, sin que nadie tenga que hacer nada por cada reserva,
hace falta que flowww tenga una opción de configuración de **"copia
interna"/"correo de notificaciones"** que se active una sola vez apuntando
a la bandeja que usa el bot — está pendiente de confirmar si existe. El
correo tampoco trae el teléfono de la paciente, así que por esta vía el
consentimiento solo se puede mandar por correo, no por WhatsApp.

Configuración (`.env`):

```
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_IMAP_USER=bandeja-del-bot@gmail.com
EMAIL_IMAP_PASSWORD=una-contraseña-de-aplicación
EMAIL_IMAP_FOLDER=INBOX
FLOWWW_SENDER_EMAIL=noreply@flowww.com
```

Un job en segundo plano revisa esa bandeja cada 5 minutos (mismo scheduler
que los recordatorios, ver `app/scheduler.py`), marca cada correo como
leído tras procesarlo, y es seguro reprocesar por error porque cada cita se
deduplica con un id derivado de código de paciente + fecha + hora.

## Pendiente antes de producción

- **Textos legales reales**: los dos tratamientos de ejemplo (`Depilación
  láser`, `Peeling químico`) llevan un texto placeholder marcado como tal.
  Hay que sustituirlos por el consentimiento informado real que la clínica
  ya usa (o encargar su redacción a su equipo médico/legal).
- **Credenciales de envío**: cuenta de Twilio WhatsApp Business (o Meta Cloud
  API) y un servidor SMTP real.
- **Validación legal de la firma**: el flujo captura firma dibujada + IP +
  timestamp + hash del PDF como evidencia. Para tratamientos médicos es
  recomendable que un abogado confirme que esto es suficiente para el país
  donde opera la clínica, y revisar la política de retención de estos datos
  de salud (categoría especial bajo GDPR/LOPD).
- **Base de datos**: en producción, cambiar `DATABASE_URL` de SQLite a
  Postgres (en Render, añade su addon de Postgres gestionado y usa la URL
  que te da).
- **Login del admin**: fija `ADMIN_USER`/`ADMIN_PASSWORD` en el entorno de
  producción; si se deja vacío, la contraseña cambia cada vez que el
  servidor reinicia (solo pensado para pruebas).
- **Integración con flowww**: pendiente de confirmar si la clínica tiene el
  plan que habilita su API/webhooks, o si hay que usar el atajo del correo de
  confirmación. El código receptor ya está listo (ver sección de arriba),
  falta conectar la fuente real de datos.
- **`WEBHOOK_SECRET`**: fija un valor largo y aleatorio en producción antes
  de darle la URL del webhook a flowww/Zapier.
