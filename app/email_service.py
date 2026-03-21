"""
Servicio de Email — Gmail SMTP
Envía notificaciones HTML de login exitoso y alertas de seguridad.
"""

import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)

# ─── Config Gmail SMTP ────────────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "tu_correo@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "xxxx xxxx xxxx xxxx")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Envía un email HTML vía Gmail SMTP (TLS)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Sistema de Autenticación <{GMAIL_USER}>"
    msg["To"] = to_email

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

    return True


# ─── Template: Login exitoso ──────────────────────────────────────────────────
def _template_login_exitoso(nombre: str, ip: str, hora: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:12px;
                      box-shadow:0 4px 20px rgba(0,0,0,0.08);overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a73e8,#0d47a1);
                       padding:36px 40px;text-align:center;">
              <div style="font-size:40px;margin-bottom:10px;">🔐</div>
              <h1 style="color:#ffffff;margin:0;font-size:24px;font-weight:700;
                         letter-spacing:-0.5px;">Inicio de Sesión Detectado</h1>
              <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;font-size:14px;">
                Notificación de seguridad
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="font-size:16px;color:#333;margin:0 0 20px;">
                Hola, <strong>{nombre}</strong> 👋
              </p>
              <p style="font-size:15px;color:#555;line-height:1.6;margin:0 0 28px;">
                Se ha iniciado sesión correctamente en tu cuenta. Si fuiste tú, 
                no necesitas hacer nada. Si <strong>no reconoces</strong> este acceso, 
                cambia tu contraseña inmediatamente.
              </p>

              <!-- Info box -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f0f7ff;border-left:4px solid #1a73e8;
                            border-radius:0 8px 8px 0;margin-bottom:28px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0 0 10px;font-size:13px;font-weight:700;
                               color:#1a73e8;text-transform:uppercase;letter-spacing:0.5px;">
                      Detalles del acceso
                    </p>
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:5px 0;font-size:14px;color:#555;width:130px;">
                          📅 Fecha y hora:
                        </td>
                        <td style="padding:5px 0;font-size:14px;color:#222;font-weight:600;">
                          {hora}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:5px 0;font-size:14px;color:#555;">
                          🌐 Dirección IP:
                        </td>
                        <td style="padding:5px 0;font-size:14px;color:#222;font-weight:600;">
                          {ip}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- CTA -->
              <div style="text-align:center;">
                <a href="#"
                   style="display:inline-block;background:#1a73e8;color:#fff;
                          padding:14px 36px;border-radius:8px;text-decoration:none;
                          font-size:15px;font-weight:600;letter-spacing:0.3px;">
                  Cambiar contraseña
                </a>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f9fa;padding:24px 40px;text-align:center;
                       border-top:1px solid #e8eaed;">
              <p style="margin:0;font-size:12px;color:#9aa0a6;line-height:1.6;">
                Este email fue enviado automáticamente por el sistema de seguridad.<br>
                © {datetime.utcnow().year} API Gestión Académica — Maestría
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# ─── Template: Alerta login fallido ──────────────────────────────────────────
def _template_login_fallido(nombre: str, ip: str, hora: str, intentos: int) -> str:
    barra_pct = min(int((intentos / 5) * 100), 100)
    color_barra = "#f44336" if intentos >= 4 else "#ff9800" if intentos >= 3 else "#ffc107"

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#fff8f7;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff8f7;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:12px;
                      box-shadow:0 4px 20px rgba(244,67,54,0.12);overflow:hidden;
                      border-top:5px solid #f44336;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#f44336,#b71c1c);
                       padding:36px 40px;text-align:center;">
              <div style="font-size:48px;margin-bottom:10px;">⚠️</div>
              <h1 style="color:#ffffff;margin:0;font-size:24px;font-weight:700;">
                Alerta de Seguridad
              </h1>
              <p style="color:rgba(255,255,255,0.85);margin:8px 0 0;font-size:14px;">
                Se detectaron intentos de acceso no autorizados
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="font-size:16px;color:#333;margin:0 0 16px;">
                Hola, <strong>{nombre}</strong>
              </p>
              <p style="font-size:15px;color:#555;line-height:1.6;margin:0 0 24px;">
                Hemos detectado <strong style="color:#f44336;">{intentos} intentos fallidos</strong>
                de inicio de sesión en tu cuenta. Si no eres tú, 
                te recomendamos cambiar tu contraseña de inmediato.
              </p>

              <!-- Info box -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#fff3f2;border-left:4px solid #f44336;
                            border-radius:0 8px 8px 0;margin-bottom:24px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0 0 12px;font-size:13px;font-weight:700;
                               color:#f44336;text-transform:uppercase;letter-spacing:0.5px;">
                      Detalles del intento
                    </p>
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding:5px 0;font-size:14px;color:#666;width:140px;">
                          📅 Último intento:
                        </td>
                        <td style="padding:5px 0;font-size:14px;color:#222;font-weight:600;">
                          {hora}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:5px 0;font-size:14px;color:#666;">
                          🌐 Dirección IP:
                        </td>
                        <td style="padding:5px 0;font-size:14px;color:#222;font-weight:600;">
                          {ip}
                        </td>
                      </tr>
                      <tr>
                        <td style="padding:5px 0;font-size:14px;color:#666;">
                          🔢 Nº intentos:
                        </td>
                        <td style="padding:5px 0;font-size:14px;color:#f44336;font-weight:700;">
                          {intentos} / 5
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Barra de peligro -->
              <p style="font-size:13px;color:#888;margin:0 0 8px;">
                Nivel de riesgo: <strong style="color:{color_barra};">
                  {"CRÍTICO" if intentos >= 5 else "ALTO" if intentos >= 4 else "MEDIO"}
                </strong>
              </p>
              <div style="background:#eee;border-radius:100px;height:8px;margin-bottom:28px;">
                <div style="background:{color_barra};width:{barra_pct}%;
                            height:8px;border-radius:100px;
                            transition:width 0.3s ease;"></div>
              </div>

              <!-- CTA -->
              <div style="text-align:center;">
                <a href="#"
                   style="display:inline-block;background:#f44336;color:#fff;
                          padding:14px 36px;border-radius:8px;text-decoration:none;
                          font-size:15px;font-weight:600;">
                  🔒 Proteger mi cuenta
                </a>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f9fa;padding:24px 40px;text-align:center;
                       border-top:1px solid #f5e0e0;">
              <p style="margin:0;font-size:12px;color:#9aa0a6;line-height:1.6;">
                Si fuiste tú quien intentó ingresar y olvidaste tu contraseña, 
                usa la opción de recuperación.<br>
                © {datetime.utcnow().year} API Gestión Académica — Maestría
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


# ─── Funciones públicas ───────────────────────────────────────────────────────
async def send_login_success_email(to_email: str, nombre: str, ip: str, hora: str) -> bool:
    """Envía email de notificación de login exitoso."""
    subject = "🔐 Nuevo inicio de sesión en tu cuenta"
    html = _template_login_exitoso(nombre, ip, hora)
    return _send_email(to_email, subject, html)


async def send_login_failed_email(
    to_email: str, nombre: str, ip: str, hora: str, intentos: int
) -> bool:
    """Envía alerta de seguridad por intentos de login fallidos."""
    subject = f"⚠️ Alerta: {intentos} intentos fallidos en tu cuenta"
    html = _template_login_fallido(nombre, ip, hora, intentos)
    return _send_email(to_email, subject, html)
