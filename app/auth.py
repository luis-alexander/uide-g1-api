"""
Módulo de autenticación: bcrypt hashing + JWT tokens
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-maestria-2025")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt (salt incluido automáticamente)."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(payload: dict) -> str:
    """Genera un JWT firmado con expiración."""
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    data["iat"] = datetime.utcnow()
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica y valida un JWT. Retorna None si es inválido o expirado."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
