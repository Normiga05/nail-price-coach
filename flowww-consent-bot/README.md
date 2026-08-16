# flowww Consent Bot

Bot para que las pacientes de una clínica estética firmen el consentimiento
informado de un tratamiento 100% online, sin papel, recibiendo el enlace de
firma por WhatsApp y/o correo.

Este proyecto es independiente de flowww: por ahora el staff de la clínica
crea el consentimiento manualmente en el panel (paciente + tratamiento). Una
integración directa con la API de flowww (requiere su plan "Legend") queda
como fase futura, una vez la clínica confirme qué acceso tiene.

## Flujo

1. El staff entra a `/admin/new`, elige la paciente y el tratamiento.
2. El bot genera un enlace único de firma y lo envía por WhatsApp (Twilio) y/o
   correo (SMTP).
3. La paciente abre el enlace, lee el consentimiento, escribe su nombre y
   firma con el dedo/ratón.
4. El bot genera un PDF firmado con la evidencia (IP, fecha/hora, hash del
   documento) y lo guarda. El staff lo ve y descarga desde `/admin`.

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
  plan que habilita su API, para poder traer pacientes/citas automáticamente
  en vez de crearlas a mano.
