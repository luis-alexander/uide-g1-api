#!/bin/bash
# ============================================================
#  test_login.sh — Pruebas completas del API de Login
#  Uso: bash test_login.sh [BASE_URL]
# ============================================================

BASE_URL="${1:-http://localhost:8080}"
CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  PRUEBAS API LOGIN + EMAIL${NC}"
echo -e "${CYAN}  URL: $BASE_URL${NC}"
echo -e "${CYAN}================================================${NC}\n"

# ── 1. Health ────────────────────────────────────────────────────────────────
echo -e "${CYAN}[1] GET /health${NC}"
curl -s "$BASE_URL/health" | python3 -m json.tool; echo

# ── 2. Registro ──────────────────────────────────────────────────────────────
echo -e "${CYAN}[2] POST /auth/register — Registro exitoso${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ana Torres","email":"ana.torres@gmail.com","password":"MiPass123!","rol":"estudiante"}' \
  | python3 -m json.tool; echo

# ── 3. Registro admin ────────────────────────────────────────────────────────
echo -e "${CYAN}[3] POST /auth/register — Usuario admin${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Admin Root","email":"admin@sistema.com","password":"Admin123!","rol":"admin"}' \
  | python3 -m json.tool; echo

# ── 4. Login exitoso ─────────────────────────────────────────────────────────
echo -e "${CYAN}[4] POST /auth/login — Login exitoso (envía email)${NC}"
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"ana.torres@gmail.com","password":"MiPass123!"}')
echo $LOGIN_RESP | python3 -m json.tool
TOKEN=$(echo $LOGIN_RESP | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
echo -e "\n🔑 Token: ${TOKEN:0:60}...\n"

# ── 5. Perfil autenticado ────────────────────────────────────────────────────
echo -e "${CYAN}[5] GET /auth/me — Perfil con token JWT${NC}"
curl -s "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool; echo

# ── 6. Sesiones activas ──────────────────────────────────────────────────────
echo -e "${CYAN}[6] GET /auth/sessions${NC}"
curl -s "$BASE_URL/auth/sessions" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool; echo

# ── 7. Login fallido x3 (activa alerta email) ────────────────────────────────
echo -e "${CYAN}[7] POST /auth/login — 3 intentos fallidos (activa alerta)${NC}"
for i in 1 2 3; do
  echo -e "  Intento $i:"
  curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"ana.torres@gmail.com","password":"ContraseñaMal"}' \
    | python3 -m json.tool
  echo
done

# ── 8. Cambio de contraseña ──────────────────────────────────────────────────
echo -e "${CYAN}[8] POST /auth/change-password${NC}"
curl -s -X POST "$BASE_URL/auth/change-password" \
  -H "Content-Type: application/json" \
  -d '{"email":"ana.torres@gmail.com","password_actual":"MiPass123!","password_nueva":"NuevoPass456!"}' \
  | python3 -m json.tool; echo

# ── 9. Admin: listar usuarios ────────────────────────────────────────────────
echo -e "${CYAN}[9] GET /admin/users — con token de usuario normal (403)${NC}"
curl -s "$BASE_URL/admin/users" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool; echo

# ── 10. Logout ───────────────────────────────────────────────────────────────
echo -e "${CYAN}[10] POST /auth/logout${NC}"
curl -s -X POST "$BASE_URL/auth/logout" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool; echo

# ── 11. Token inválido ────────────────────────────────────────────────────────
echo -e "${CYAN}[11] GET /auth/me con token inválido (401)${NC}"
curl -s "$BASE_URL/auth/me" \
  -H "Authorization: Bearer token-falso-123" | python3 -m json.tool; echo

# ── 12. Email duplicado ───────────────────────────────────────────────────────
echo -e "${CYAN}[12] POST /auth/register — email duplicado (400)${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Otro","email":"ana.torres@gmail.com","password":"Otro123!","rol":"estudiante"}' \
  | python3 -m json.tool; echo

# ── 13. Validación contraseña débil ──────────────────────────────────────────
echo -e "${CYAN}[13] POST /auth/register — contraseña débil (422)${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","email":"test@test.com","password":"abc","rol":"estudiante"}' \
  | python3 -m json.tool; echo

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ PRUEBAS COMPLETADAS${NC}"
echo -e "${GREEN}================================================${NC}"
