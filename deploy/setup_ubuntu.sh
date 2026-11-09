#!/usr/bin/env bash
# ==============================================================================
# BeautySchedule — Script Não-Destrutivo de Preparação para Ubuntu Linux
# ==============================================================================
# ATENÇÃO:
# - Este script NÃO apaga bancos de dados existentes nem executa DROP/TRUNCATE.
# - Sincroniza os arquivos do projeto para APP_DIR (/opt/beautyschedule por padrão),
#   cria o .venv e o .env dentro desse mesmo diretório e configura o arquivo
#   systemd com o usuário e grupo reais da VM Ubuntu.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

APP_DIR="${APP_DIR:-/opt/beautyschedule}"
APP_USER="${APP_USER:-$(id -un)}"
APP_GROUP="${APP_GROUP:-$(id -gn)}"

echo "=== [1/5] Verificando pacotes básicos do Ubuntu Linux ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip mysql-client rsync

echo "=== [2/5] Sincronizando arquivos do projeto em ${APP_DIR} ==="
sudo mkdir -p "${APP_DIR}"
sudo chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"

if [ "${REPO_ROOT}" != "${APP_DIR}" ]; then
    rsync -a --exclude '.venv' --exclude '__pycache__' --exclude '.pytest_cache' \
          --exclude '*.db' --exclude '.env' \
          "${REPO_ROOT}/" "${APP_DIR}/"
    echo "Arquivos sincronizados de ${REPO_ROOT} para ${APP_DIR}."
else
    echo "Repositório já está localizado em ${APP_DIR}."
fi

cd "${APP_DIR}"

echo "=== [3/5] Criando ambiente virtual Python em ${APP_DIR}/.venv ==="
python3 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/backend/requirements.txt"

echo "=== [4/5] Verificando arquivo ${APP_DIR}/.env ==="
if [ ! -f "${APP_DIR}/.env" ]; then
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    chmod 600 "${APP_DIR}/.env"
    echo "Arquivo ${APP_DIR}/.env criado a partir de .env.example."
    echo "IMPORTANTE: Na VM Ubuntu com MySQL 8.4, defina DB_ENGINE=mysql e a senha em ${APP_DIR}/.env."
else
    echo "Arquivo ${APP_DIR}/.env já existe (preservado sem sobrescrita)."
fi

echo "=== [5/5] Preparando unidade systemd para o usuário '${APP_USER}' ==="
RENDERED_SERVICE="${APP_DIR}/deploy/beautyschedule.service.rendered"
sed -e "s|__APP_USER__|${APP_USER}|g" \
    -e "s|__APP_GROUP__|${APP_GROUP}|g" \
    -e "s|/opt/beautyschedule|${APP_DIR}|g" \
    "${APP_DIR}/deploy/beautyschedule.service" > "${RENDERED_SERVICE}"

echo "Unidade systemd gerada em: ${RENDERED_SERVICE} (User=${APP_USER}, Group=${APP_GROUP}, WorkingDirectory=${APP_DIR})"

echo ""
echo "=============================================================================="
echo "Preparação concluída com sucesso em ${APP_DIR}!"
echo "Próximos passos manuais na VM Ubuntu:"
echo "  1. Inspecione o MySQL existente: sudo mysql -u root -p -e 'SHOW DATABASES;'"
echo "  2. Execute os scripts SQL de forma controlada:"
echo "     mysql -u root -p < ${APP_DIR}/database/01_create_database.sql"
echo "     mysql -u root -p < ${APP_DIR}/database/02_create_tables.sql"
echo "     mysql -u root -p < ${APP_DIR}/database/03_insert_data.sql"
echo "  3. Edite ${APP_DIR}/.env definindo DB_ENGINE=mysql e DB_PASSWORD"
echo "  4. Instale e inicie o serviço systemd já configurado para '${APP_USER}':"
echo "     sudo cp ${RENDERED_SERVICE} /etc/systemd/system/beautyschedule.service"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable --now beautyschedule"
echo "=============================================================================="
