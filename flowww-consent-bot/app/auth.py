"""Protección del panel /admin, donde se ven datos de pacientes (nombre, teléfono, correo).

Si no hay ADMIN_USER/ADMIN_PASSWORD en el .env, se genera una contraseña
aleatoria al arrancar y se imprime en el log, para que el panel nunca quede
abierto sin querer, ni siquiera en desarrollo.
"""

import logging
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app import config

logger = logging.getLogger("flowww_consent_bot.auth")

security = HTTPBasic()

_admin_user = config.ADMIN_USER or "admin"
_admin_password = config.ADMIN_PASSWORD
if not _admin_password:
    _admin_password = secrets.token_urlsafe(12)
    logger.warning(
        "ADMIN_PASSWORD no está configurado en .env. Contraseña temporal generada "
        "para /admin -> usuario: %s | contraseña: %s",
        _admin_user,
        _admin_password,
    )


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    valid_user = secrets.compare_digest(credentials.username, _admin_user)
    valid_password = secrets.compare_digest(credentials.password, _admin_password)
    if not (valid_user and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
