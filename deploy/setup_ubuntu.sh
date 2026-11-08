#!/usr/bin/env bash
# ==============================================================================
# BeautySchedule — Script Não-Destrutivo de Preparação para Ubuntu Linux
# ==============================================================================
# ATENÇÃO:
# - Este script NÃO apaga bancos de dados existentes nem executa DROP/TRUNCATE.
# - Os scripts SQL em database/ devem ser aplicados manualmente após inspeção
#   do MySQL 8.4 na VM Ubuntu.
# ==============================================================================

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/beautyschedule}"

echo "=== [1/4] Verificando pacotes básicos do Ubuntu Linux ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip mysql-client

echo "=== [2/4] Preparando diretório da aplicação em ${APP_DIR} ==="
if [ ! -d "${APP_DIR}" ]; then
    sudo mkdir -p "${APP_DIR}"
    sudo chown -R "$USER":"$USER" "${APP_DIR}"
fi

echo "=== [3/4] Criando ambiente virtual Python e instalando dependências ==="
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== [4/4] Verificando arquivo .env ==="
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Arquivo .env criado a partir de .env.example."
    echo "IMPORTANTE: Edite o arquivo .env com as credenciais reais do MySQL 8.4 da VM."
else
    echo "Arquivo .env já existe (preservado sem sobrescrita)."
fi

echo ""
echo "=============================================================================="
echo "Preparação concluída com sucesso!"
echo "Próximos passos manuais na VM Ubuntu:"
echo "  1. Inspecione o MySQL existente: sudo mysql -u root -p -e 'SHOW DATABASES;'"
echo "  2. Execute os scripts SQL de forma controlada:"
echo "     mysql -u root -p < database/01_create_database.sql"
echo "     mysql -u root -p < database/02_create_tables.sql"
echo "     mysql -u root -p < database/03_insert_data.sql"
echo "  3. Ajuste DB_ENGINE=mysql e a senha no arquivo .env"
echo "  4. Inicie ou registre o serviço systemd (deploy/beautyschedule.service)"
echo "=============================================================================="
