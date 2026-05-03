# Trabajo Final — Módulo de Tratamiento de Datos
## Respuestas a las preguntas de retroalimentación

---

## 1. Actualmente usan una base de datos en memoria, y dicen que en produccion usarian una bdd como PostgreSQL. Que consideraciones deben tomar para elegir la base de datos y donde reposaria esta misma?

### Contexto del proyecto

La API `uide-g1-api` es un sistema de autenticación segura construido con **FastAPI + Python**, que actualmente almacena toda la información de usuarios, sesiones e intentos de login en memoria, a través del archivo `database.py`. Esto funciona en desarrollo, pero presenta problemas críticos para un entorno productivo.

---
INTEGRANTE: Alejandra Tello
### ¿Por qué la base de datos en memoria no es viable en producción?
Una base de datos en memoria no es adecuada para soportar datos críticos en producción desde una perspectiva de seguridad de la información, ya que carece de persistencia, lo que provoca la pérdida total de información ante reinicios o despliegues, afectando directamente usuarios, sesiones y configuraciones; adicionalmente, en entornos escalables genera inconsistencias al no compartir estado entre múltiples instancias, debilitando el control de acceso; esta limitación compromete la trazabilidad y la auditoría, dado que el historial de sesiones (/auth/sessions), direcciones IP y horarios no se conservan, mientras que mecanismos de seguridad como el conteo de intentos fallidos y el bloqueo de cuentas se vuelven inefectivos al reiniciarse; finalmente, la ausencia de respaldos y capacidades de recuperación ante fallos representa un riesgo crítico para la continuidad del negocio y el cumplimiento, al exponer a la organización a una pérdida total de datos ante cualquier incidente.

### ¿Por qué elegir PostgreSQL para este proyecto?

Dado que el proyecto maneja **usuarios, sesiones, roles (`estudiante`/`admin`), historial de IPs y contadores de intentos fallidos**, los datos son claramente relacionales y estructurados. PostgreSQL es la elección más sólida porque:

**1. Garantías ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad)**
El bloqueo automático de cuentas tras 5 intentos fallidos requiere que las escrituras sean atómicas y consistentes. Con una base de datos en memoria, una condición de carrera podría permitir más intentos de los permitidos. PostgreSQL garantiza que esto no ocurra.

**2. Integridad referencial**
Las sesiones deben estar vinculadas a un usuario válido. Con claves foráneas, si se elimina un usuario, sus sesiones se eliminan en cascada, manteniendo la base de datos limpia.

**3. Soporte nativo de tipos útiles para este proyecto**
- `TIMESTAMP WITH TIME ZONE` para los registros de login en UTC (ya usado en el proyecto).
- `BOOLEAN` para el campo `is_blocked`.
- `INET` para almacenar direcciones IP de forma eficiente.

**4. Integración nativa con FastAPI**
El ecosistema Python/FastAPI tiene soporte maduro para PostgreSQL mediante **SQLAlchemy** (ORM) y **Alembic** (migraciones), lo que permite versionar los cambios al esquema de la base de datos de forma ordenada.

**5. Seguridad**
PostgreSQL soporta encriptación de conexiones (SSL/TLS), autenticación por roles y auditoría, lo que complementa el sistema de seguridad ya implementado en la API (bcrypt, JWT, alertas por email).

### ¿Dónde reposaría la base de datos en producción?

La base de datos **debe estar desacoplada del contenedor de la API**. Nunca deben correr en el mismo proceso ni en el mismo contenedor. Hay tres opciones ordenadas por recomendación:

#### ✅ — Servicio gestionado en la nube.

| Proveedor | Servicio | Ventaja principal |
|---|---|---|
| **Supabase** | PostgreSQL gestionado | Tier gratuito generoso, ideal para proyectos académicos y startups |
| **Railway** | PostgreSQL gestionado | Muy fácil de integrar con proyectos Dockerizados |
| **AWS RDS** | Amazon RDS for PostgreSQL | Estándar empresarial, alta disponibilidad, backups automáticos |
| **Google Cloud SQL** | Cloud SQL for PostgreSQL | Integración con otros servicios de GCP |
| **Azure Database** | Azure for PostgreSQL | Opción para ecosistemas Microsoft |

**Ventajas:**
- Backups automáticos diarios con retención configurable.
- Actualizaciones de seguridad gestionadas por el proveedor.
- Alta disponibilidad con réplicas automáticas.
- Escalado vertical sin tiempo de inactividad.
- Sin necesidad de gestionar el servidor de base de datos.

### Resumen de la decisión

| Criterio | Decisión |
|---|---|
| Motor de base de datos | **PostgreSQL** |
| Razón principal | Datos relacionales, garantías ACID, integración nativa con FastAPI |
| Dónde alojar en producción | Servicio gestionado en la nube (Supabase o AWS RDS) |
| Dónde alojar en desarrollo | Docker Compose con volumen persistente (ya integrado en el proyecto) |
| Integración con FastAPI/Python | SQLAlchemy (ORM) + Alembic (migraciones) |
| Gestión de credenciales | Variables de entorno en `.env` (ya implementado en el proyecto) |
| Datos que migran de memoria a BD | Usuarios, sesiones, historial de IPs, contadores de intentos fallidos |

---
INTEGRANTE: Luis Alexander Soto Segovia

Para elegir la base de datos en producción se deben considerar factores como el volumen de datos esperado, la cantidad de usuarios concurrentes, la seguridad, la integridad de la información, la facilidad de respaldo y recuperación, el rendimiento de las consultas y la escalabilidad futura del sistema.

En este caso, PostgreSQL sería una buena opción porque permite manejar datos persistentes, relaciones entre tablas, transacciones seguras y control de acceso. Además, es importante definir dónde reposará la base de datos: puede estar en un servidor propio de la institución, en una máquina virtual, en un contenedor dedicado o en un servicio administrado en la nube, dependiendo de los recursos disponibles y las políticas de seguridad.

**Que consideraciones deben tomar en cuenta para el almacenamiento y transporte de datos para prevenir ataques?**

- **Consideraciones para almacenamiento seguro de datos:**
- Cifrado en reposo: proteger la información almacenada (ej. discos cifrados en PostgreSQL).
- Control de accesos: uso de roles, privilegios mínimos y autenticación fuerte.
- Backups seguros: copias cifradas y almacenadas en ubicaciones separadas.
- Actualizaciones y parches: mantener la base de datos y sistema al día.
- Segmentación de red: aislar la base de datos del acceso público.

- **Consideraciones para transporte seguro de datos:**
- Cifrado en tránsito: uso de protocolos seguros como TLS (HTTPS).
- Uso de VPN: para conexiones internas o administrativas seguras.
- Validación de certificados: evitar ataques de tipo “man-in-the-middle”.
- Autenticación segura: uso de tokens, OAuth o credenciales robustas.
- Protección contra interceptación: evitar enviar datos sensibles en texto plano.

En producción, lo ideal es usar una base de datos como PostgreSQL en un entorno separado de la aplicación, con acceso seguro y backups configurados.
