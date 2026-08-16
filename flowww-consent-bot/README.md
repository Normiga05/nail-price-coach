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

Abre `http://localhost:8000/admin`.

Sin credenciales de Twilio/SMTP en `.env`, el envío de WhatsApp y correo
corre en **modo simulado**: no se envía nada real, solo queda en el log del
servidor (`[MOCK WhatsApp]` / `[MOCK Email]`). Esto permite probar todo el
flujo (crear consentimiento → firmar → generar PDF) sin cuentas reales.

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
  Postgres.
- **Integración con flowww**: pendiente de confirmar si la clínica tiene el
  plan que habilita su API, para poder traer pacientes/citas automáticamente
  en vez de crearlas a mano.
