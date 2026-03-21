# 🔐 API de Autenticación con Notificaciones por Email

> **Trabajo de Maestría v2.0** — Sistema de login seguro con bcrypt, JWT y alertas por Gmail SMTP.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?style=flat&logo=docker)](https://docker.com)
[![Gmail](https://img.shields.io/badge/Gmail-SMTP-EA4335?style=flat&logo=gmail)](https://gmail.com)

---

## 🚀 Funcionalidades

| Función | Detalle |
|---|---|
| 🔒 Registro seguro | Contraseña hasheada con **bcrypt** (salt rounds=12) |
| 🎫 Login con JWT | Tokens firmados con expiración configurable |
| 📧 Email login exitoso | Notificación HTML con IP y hora exacta |
| ⚠️ Alerta de seguridad | Email de alerta tras 3+ intentos fallidos |
| 🚫 Bloqueo de cuenta | Bloqueo automático tras 5 intentos fallidos |
| 👤 Perfil autenticado | Endpoint protegido `/auth/me` |
| 📋 Historial de sesiones | Registro de IPs y horarios |
| 🔑 Cambio de contraseña | Con verificación de contraseña actual |
| 👑 Panel admin | Listado de usuarios para rol admin |

---

## 📁 Estructura del proyecto

```
api-login/
├── app/
│   ├── main.py           # Endpoints FastAPI
│   ├── auth.py           # bcrypt + JWT
│   ├── email_service.py  # Gmail SMTP + templates HTML
│   └── database.py       # Base de datos en memoria
├── Dockerfile
├── .env.example          # Variables de entorno (plantilla)
├── .gitignore
├── requirements.txt
├── test_login.sh         # Pruebas con curl
└── README.md
```

---

## ⚙️ Configuración de Gmail

> ⚠️ **IMPORTANTE**: No uses tu contraseña normal de Gmail. Debes crear una **Contraseña de Aplicación**.

### Pasos para obtener la App Password de Gmail:

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. **Seguridad** → **Verificación en 2 pasos** (debe estar activada)
3. **Contraseñas de aplicaciones** → Selecciona "Otra (nombre personalizado)"
4. Escribe `API Maestría` → Haz clic en **Generar**
5. Copia el código de 16 caracteres (ej: `abcd efgh ijkl mnop`)

### Configurar el .env:
```bash
cp .env.example .env
# Editar .env con tus datos:
GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
JWT_SECRET=mi-clave-secreta-segura
```

---

## 💻 Instalación local

```bash
# 1. Clonar
git clone https://github.com/TU_USUARIO/api-login.git
cd api-login

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Configurar variables
cp .env.example .env
# Editar .env con tus credenciales Gmail

# 5. Ejecutar
uvicorn app.main:app --reload --port 8080
```

---

## 🐳 Docker

```bash
# Construir imagen
docker build -t api-login:latest .

# Ejecutar con variables de entorno
docker run -d \
  --name api-login \
  -p 8080:8080 \
  -e GMAIL_USER=tu_correo@gmail.com \
  -e GMAIL_APP_PASSWORD="abcd efgh ijkl mnop" \
  -e JWT_SECRET=mi-clave-secreta \
  api-login:latest

# Verificar
docker logs api-login
curl http://localhost:8080/health
```

---

## 🔌 Endpoints

### Públicos
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Info del API |
| `GET` | `/health` | Estado del sistema |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/auth/register` | Registrar usuario |
| `POST` | `/auth/login` | **Login + envío de email** |
| `POST` | `/auth/change-password` | Cambiar contraseña |

### Protegidos (requieren JWT)
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/auth/me` | Perfil del usuario |
| `GET` | `/auth/sessions` | Sesiones activas |
| `POST` | `/auth/logout` | Cerrar sesión |
| `GET` | `/admin/users` | Usuarios (solo admin) |

---

## 📧 Emails que se envían

### ✅ Login exitoso
Se envía al email del usuario al iniciar sesión correctamente.

```
Asunto: 🔐 Nuevo inicio de sesión en tu cuenta
Contenido:
  - Nombre del usuario
  - IP desde donde se conectó
  - Fecha y hora exacta (UTC)
  - Botón para cambiar contraseña
```

### ⚠️ Alerta de seguridad (login fallido)
Se envía a partir del **3er intento fallido** consecutivo.

```
Asunto: ⚠️ Alerta: N intentos fallidos en tu cuenta
Contenido:
  - Número de intentos fallidos
  - IP del atacante
  - Fecha y hora del último intento
  - Barra de nivel de riesgo (MEDIO / ALTO / CRÍTICO)
  - Botón para proteger la cuenta
```

---

## 🧪 Pruebas con curl

```bash
# Ejecutar todas las pruebas
bash test_login.sh http://localhost:8080

# Registro
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Torres","email":"ana@gmail.com","password":"MiPass123!","rol":"estudiante"}'

# Login (dispara email)
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@gmail.com","password":"MiPass123!"}'

# Perfil (con JWT)
curl http://localhost:8080/auth/me \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## ☁️ Despliegue en Cloud Run

```bash
# Build y push
gcloud builds submit --tag gcr.io/TU-PROJECT/api-login

# Deploy con variables de entorno
gcloud run deploy api-login \
  --image gcr.io/TU-PROJECT/api-login \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars \
    GMAIL_USER=tu_correo@gmail.com,\
    GMAIL_APP_PASSWORD="abcd efgh ijkl mnop",\
    JWT_SECRET=mi-clave-secreta
```

---

## 🌿 Branches del proyecto

```
main
├── feature/auth-bcrypt     → Hash con bcrypt rounds=12 ✅
├── feature/jwt-tokens      → Sistema JWT con expiración ✅
└── feature/email-alerts    → Gmail SMTP + templates HTML ✅
```

```bash
# Flujo de trabajo
git checkout -b feature/email-alerts
git add .
git commit -m "feat: add Gmail SMTP login notifications"
git push origin feature/email-alerts
# → Pull Request → Merge a main
```

---

## 🔑 Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `GMAIL_USER` | — | Tu correo Gmail |
| `GMAIL_APP_PASSWORD` | — | App Password de Gmail (16 chars) |
| `JWT_SECRET` | `super-secret-key-...` | Clave de firma JWT |
| `JWT_EXPIRE_HOURS` | `24` | Horas de validez del token |
| `PORT` | `8080` | Puerto del servidor |

---

## 📸 Evidencias

### 1. API local en /docs
*(Captura Swagger UI en http://localhost:8080/docs)*

### 2. Docker build
```
docker build -t api-login:latest .
[+] Building 52.3s ✅
```

### 3. Email recibido — Login exitoso
*(Captura del email en bandeja de entrada)*

### 4. Email recibido — Alerta de seguridad
*(Captura del email de alerta con barra de riesgo)*

### 5. Cloud Run activo
*(Captura consola GCP - servicio api-login ACTIVO)*

---

## 🛠 Tecnologías

| Tech | Uso |
|---|---|
| FastAPI 0.111 | Framework web |
| bcrypt 4.1 | Hash de contraseñas |
| PyJWT 2.8 | Tokens JWT |
| Gmail SMTP | Notificaciones email |
| Docker | Contenerización |
| Google Cloud Run | Despliegue serverless |
