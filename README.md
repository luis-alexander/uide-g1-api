## 1. 🔐 API de Autenticación con Notificaciones por Email

> **Trabajo de Maestría - Tratamiento de Datos** — Sistema de login seguro con bcrypt, JWT y alertas por Gmail SMTP.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?style=flat&logo=docker)](https://docker.com)
[![Gmail](https://img.shields.io/badge/Gmail-SMTP-EA4335?style=flat&logo=gmail)](https://gmail.com)

---

## 2. 🚀 Funcionalidades

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

## 3. 📁 Estructura del proyecto

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

## Estructura de ramas del repositorio 
### A continuación se presentan las ramas que fueron creadas: 

1. Main -> Rama principal o de produccion 
2. develop-AT -> Rama de desarrollador Alejandra Tello
3. develop-LS -> Rama de desarrollador Luis Soto
4. develop-EB -> Rama de desarrollador Elvis Borbor


---

## 4. ⚙️ Configuración de Gmail

### Pasos para obtener la App Password de Gmail:

1. Ve a [myaccount.google.com](https://myaccount.google.com)
2. **Seguridad** → **Verificación en 2 pasos** (debe estar activada)
3. **Contraseñas de aplicaciones** → Selecciona "Otra (nombre personalizado)"
4. Escribe `API Maestría` → Haz clic en **Generar**
5. Copia el código de 16 caracteres (ej: `abcd efgh ijkl mnop`)

5. Configurar el .env:
```bash
cp .env.example .env
# Editar .env con tus datos:
GMAIL_USER=tu_correo@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
JWT_SECRET=mi-clave-secreta-segura
```

---

## 6. 💻 Instalación local

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

## 7. 🐳 Docker

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

## 8. 🔌 Endpoints

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

## 9. 📧 Emails que se envían

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

## 10. 🧪 Pruebas con curl

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

## 11. ☁️ Despliegue en Cloud Run

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

## 12. 🌿 Branches del proyecto

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

## 13. 🔑 Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `GMAIL_USER` | — | Tu correo Gmail |
| `GMAIL_APP_PASSWORD` | — | App Password de Gmail (16 chars) |
| `JWT_SECRET` | `super-secret-key-...` | Clave de firma JWT |
| `JWT_EXPIRE_HOURS` | `24` | Horas de validez del token |
| `PORT` | `8080` | Puerto del servidor |

---

## 14. 📸 Evidencias

 ### 1. API funcionando localmente en /docs
> Swagger UI en http://localhost:8080/docs
<img width="886" height="470" alt="image" src="https://github.com/user-attachments/assets/cf8afaae-8519-488a-9657-a9e26968d2ce" />
<img width="886" height="316" alt="image" src="https://github.com/user-attachments/assets/1325bf48-acf4-4fdd-b2a3-d1a45625d4f5" />


 ### 2. Construcción de imagen Dockerizada
```
docker build -t api-login:latest .
[+] Building 52.3s ✅
```
<img width="886" height="506" alt="image" src="https://github.com/user-attachments/assets/5c871ff4-ea69-4f6f-a6c8-7c91145cd6e3" />

### 3. Contenedor ejecutándose 
> Resultado del comando `docker ps`
<img width="886" height="49" alt="image" src="https://github.com/user-attachments/assets/be36c39c-d21a-470e-8fd0-d96209042d37" />

### 4. Prueba curl — GET /health
<img width="886" height="42" alt="image" src="https://github.com/user-attachments/assets/e1afdaa3-8ec8-4ce0-95a0-47cda48a1b49" />

### 5. Prueba curl — POST /auth/register
<img width="886" height="107" alt="image" src="https://github.com/user-attachments/assets/a89f4378-bde7-4535-8c1f-d2daaa35535f" />

### 6. Prueba curl — POST /auth/login
<img width="886" height="75" alt="image" src="https://github.com/user-attachments/assets/dc28ae32-6db9-4d5c-8e6d-e7c915663e5b" />

### 7. Prueba curl — GET /admin/users
<img width="886" height="56" alt="image" src="https://github.com/user-attachments/assets/aed9e98f-6f47-45d6-ad64-0b29dfd3b099" />

### 8. Manejo de errores (400 y 401)
> Error 400 (email duplicado)
<img width="886" height="100" alt="image" src="https://github.com/user-attachments/assets/ee38ad48-4722-4b15-bdbd-42708b2ab49c" />

> Error 401 (login fallido)
<img width="886" height="108" alt="image" src="https://github.com/user-attachments/assets/92c8e51e-8a74-4fe0-8172-7bda63fbf0a1" />

### 9. Email recibido — Login exitoso
<img width="886" height="104" alt="image" src="https://github.com/user-attachments/assets/ce4bd5b7-d99f-42a7-ac42-8eb750b7330c" />
<img width="886" height="75" alt="image" src="https://github.com/user-attachments/assets/01c7837a-9906-4eb6-8b5e-2bf90d702046" />
<img width="886" height="503" alt="image" src="https://github.com/user-attachments/assets/367a4f45-27a7-49ca-8ea1-b1e4424f72e2" />

### 10. Email recibido — Alerta de seguridad

<img width="886" height="108" alt="image" src="https://github.com/user-attachments/assets/bb1ee1d5-d557-4fcb-b33c-2dd526246f23" />
<img width="886" height="584" alt="image" src="https://github.com/user-attachments/assets/f9cd286b-3873-426f-a407-6ae7fe463174" />


### 11. Imagen subida a Container Registry
<img width="886" height="284" alt="image" src="https://github.com/user-attachments/assets/2603c02d-cda5-4290-b283-aed66b6f37fb" />

### 12. API desplegada en Cloud Run
<img width="1918" height="602" alt="image" src="https://github.com/user-attachments/assets/f59aa612-9c54-46ea-b50f-c3f2136bf3e6" />
<img width="886" height="71" alt="image" src="https://github.com/user-attachments/assets/17c38e64-384d-4920-bcd1-2f12d3c7199e" />
<img width="886" height="503" alt="image" src="https://github.com/user-attachments/assets/ae59603f-779e-49fe-a8ab-87b0e435ac85" />

### 13. Endpoint público accesible

<img width="1919" height="334" alt="image" src="https://github.com/user-attachments/assets/0146ba16-ce47-4cf3-87d9-74d6d5696fe7" />

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
