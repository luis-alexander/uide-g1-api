"""
Base de datos en memoria (para demo/desarrollo).
En producción reemplazar por PostgreSQL, MongoDB, etc.
"""

# Usuarios registrados: { user_id: {...} }
users_db: dict = {}

# Sesiones activas: { session_id: {...} }
sessions_db: dict = {}

# Intentos fallidos: { email: count }
failed_attempts_db: dict = {}
