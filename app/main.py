"""
API de Autenticación con Notificaciones por Email
Stack: FastAPI + bcrypt + Gmail SMTP
Autor: Maestría DevOps/Cloud
"""

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import uuid
import logging
import secrets
import string

from app.auth import hash_password, verify_password, create_token, decode_token
from app.email_service import send_login_success_email, send_login_failed_email
from app.database import users_db, sessions_db, failed_attempts_db

# ─── Logging estructurado ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}'
)
logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="API de Autenticación",
    description="Login seguro con bcrypt, JWT y notificaciones por Gmail SMTP.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

MAX_FAILED_ATTEMPTS = 5

# ─── Modelos ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, example="Ana Torres")
    email: str = Field(..., example="ana.torres@gmail.com")
    password: str = Field(..., min_length=8, example="MiPassword123!")
    rol: Optional[str] = Field("estudiante", example="estudiante")

    @validator("email")
    def email_valido(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Email inválido")
        return v.lower().strip()

    @validator("password")
    def password_segura(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

class LoginRequest(BaseModel):
    email: str = Field(..., example="ana.torres@gmail.com")
    password: str = Field(..., example="MiPassword123!")

class ChangePasswordRequest(BaseModel):
    email: str
    password_actual: str
    password_nueva: str = Field(..., min_length=8)

    @validator("password_nueva")
    def password_segura(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Token requerido")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    user_id = payload.get("sub")
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return users_db[user_id]

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def raiz():
    return {
        "api": "Sistema de Autenticación",
        "version": "2.0.0",
        "status": "✅ Operativo",
        "docs": "/docs",
        "endpoints": {
            "POST /auth/register": "Registrar nuevo usuario",
            "POST /auth/login": "Iniciar sesión",
            "POST /auth/logout": "Cerrar sesión",
            "POST /auth/change-password": "Cambiar contraseña",
            "GET  /auth/me": "Perfil del usuario autenticado",
            "GET  /auth/sessions": "Sesiones activas del usuario",
            "GET  /admin/users": "Listar todos los usuarios (admin)",
        }
    }

@app.get("/health", tags=["General"])
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "usuarios_registrados": len(users_db),
        "sesiones_activas": len(sessions_db)
    }

# ── Registro ──────────────────────────────────────────────────────────────────
@app.post("/auth/register", status_code=201, tags=["Auth"])
async def register(data: RegisterRequest, request: Request):
    """Registra un nuevo usuario con contraseña hasheada."""
    # Verificar email duplicado
    for u in users_db.values():
        if u["email"] == data.email:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

    user_id = str(uuid.uuid4())[:8]
    user = {
        "id": user_id,
        "nombre": data.nombre,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "rol": data.rol,
        "activo": True,
        "creado_en": datetime.utcnow().isoformat(),
        "ultimo_login": None,
    }
    users_db[user_id] = user
    logger.info(f"Usuario registrado: {user_id} | {data.email}")

    return {
        "mensaje": "✅ Usuario registrado exitosamente",
        "usuario": {
            "id": user_id,
            "nombre": data.nombre,
            "email": data.email,
            "rol": data.rol,
            "creado_en": user["creado_en"]
        }
    }

# ── Login ─────────────────────────────────────────────────────────────────────
@app.post("/auth/login", tags=["Auth"])
async def login(data: LoginRequest, request: Request):
    """
    Autentica al usuario y envía notificación por email.
    - Login exitoso → email con IP y hora
    - Login fallido → email de alerta tras 3+ intentos
    """
    ip = get_client_ip(request)
    hora = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    email_lower = data.email.lower().strip()

    # Buscar usuario
    user = None
    for u in users_db.values():
        if u["email"] == email_lower:
            user = u
            break

    # ── LOGIN FALLIDO ──────────────────────────────────────────────────────────
    if not user or not verify_password(data.password, user["password_hash"]):
        # Registrar intento fallido
        failed_attempts_db[email_lower] = failed_attempts_db.get(email_lower, 0) + 1
        intentos = failed_attempts_db[email_lower]

        logger.warning(f"Login fallido: {email_lower} | IP: {ip} | Intento #{intentos}")

        # Enviar alerta por email a partir del intento #3
        if intentos >= 3 and user:
            try:
                await send_login_failed_email(
                    to_email=user["email"],
                    nombre=user["nombre"],
                    ip=ip,
                    hora=hora,
                    intentos=intentos
                )
                logger.info(f"Alerta de seguridad enviada a: {user['email']}")
            except Exception as e:
                logger.error(f"Error enviando alerta email: {e}")

        # Bloquear cuenta tras MAX intentos
        if intentos >= MAX_FAILED_ATTEMPTS:
            raise HTTPException(
                status_code=403,
                detail=f"Cuenta bloqueada temporalmente tras {MAX_FAILED_ATTEMPTS} intentos fallidos. Revisa tu email."
            )

        raise HTTPException(
            status_code=401,
            detail=f"Credenciales incorrectas. Intento {intentos}/{MAX_FAILED_ATTEMPTS}"
        )

    # ── LOGIN EXITOSO ─────────────────────────────────────────────────────────
    if not user["activo"]:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    # Limpiar intentos fallidos
    failed_attempts_db.pop(email_lower, None)

    # Generar token JWT
    token = create_token({"sub": user["id"], "email": user["email"], "rol": user["rol"]})

    # Registrar sesión
    session_id = str(uuid.uuid4())[:12]
    sessions_db[session_id] = {
        "session_id": session_id,
        "user_id": user["id"],
        "email": user["email"],
        "ip": ip,
        "hora_login": hora,
        "token": token,
        "activa": True
    }

    # Actualizar último login
    users_db[user["id"]]["ultimo_login"] = hora
    logger.info(f"Login exitoso: {email_lower} | IP: {ip} | Session: {session_id}")

    # Enviar email de notificación de login exitoso
    email_enviado = False
    try:
        await send_login_success_email(
            to_email=user["email"],
            nombre=user["nombre"],
            ip=ip,
            hora=hora
        )
        email_enviado = True
        logger.info(f"Email de login enviado a: {user['email']}")
    except Exception as e:
        logger.error(f"Error enviando email de login: {e}")

    return {
        "mensaje": "✅ Login exitoso",
        "token": token,
        "token_type": "Bearer",
        "email_notificacion": "enviado" if email_enviado else "error_al_enviar",
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"],
            "ultimo_login": hora
        }
    }

# ── Logout ────────────────────────────────────────────────────────────────────
@app.post("/auth/logout", tags=["Auth"])
def logout(current_user: dict = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Invalida la sesión activa del usuario."""
    token = credentials.credentials
    for sid, session in sessions_db.items():
        if session["token"] == token:
            sessions_db[sid]["activa"] = False
            break
    logger.info(f"Logout: {current_user['email']}")
    return {"mensaje": "✅ Sesión cerrada correctamente"}

# ── Perfil ────────────────────────────────────────────────────────────────────
@app.get("/auth/me", tags=["Auth"])
def me(current_user: dict = Depends(get_current_user)):
    """Retorna el perfil del usuario autenticado (sin password hash)."""
    return {
        "id": current_user["id"],
        "nombre": current_user["nombre"],
        "email": current_user["email"],
        "rol": current_user["rol"],
        "activo": current_user["activo"],
        "creado_en": current_user["creado_en"],
        "ultimo_login": current_user["ultimo_login"]
    }

# ── Sesiones ──────────────────────────────────────────────────────────────────
@app.get("/auth/sessions", tags=["Auth"])
def mis_sesiones(current_user: dict = Depends(get_current_user)):
    """Lista todas las sesiones del usuario autenticado."""
    mis = [
        {k: v for k, v in s.items() if k != "token"}
        for s in sessions_db.values()
        if s["user_id"] == current_user["id"]
    ]
    return {"total": len(mis), "sesiones": mis}

# ── Cambiar contraseña ────────────────────────────────────────────────────────
@app.post("/auth/change-password", tags=["Auth"])
def change_password(data: ChangePasswordRequest):
    """Cambia la contraseña del usuario tras verificar la actual."""
    user = None
    for u in users_db.values():
        if u["email"] == data.email.lower():
            user = u
            break

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(data.password_actual, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")

    users_db[user["id"]]["password_hash"] = hash_password(data.password_nueva)
    logger.info(f"Contraseña cambiada: {user['email']}")
    return {"mensaje": "✅ Contraseña actualizada correctamente"}

# ── Admin: listar usuarios ────────────────────────────────────────────────────
@app.get("/admin/users", tags=["Admin"])
def listar_usuarios(current_user: dict = Depends(get_current_user)):
    """Lista todos los usuarios (requiere rol admin)."""
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: se requiere rol admin")

    return {
        "total": len(users_db),
        "usuarios": [
            {k: v for k, v in u.items() if k != "password_hash"}
            for u in users_db.values()
        ]
    }
