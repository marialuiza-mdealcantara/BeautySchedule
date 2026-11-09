"""Testes de funcionamento básico da API, contexto do salão e isolamento SaaS."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["aplicacao"] == "BeautySchedule"
    assert body["ambiente"] == "testing"


def test_serve_frontend_index(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "BeautySchedule" in response.text


def test_obter_salao_e_horarios_funcionamento(client: TestClient) -> None:
    response = client.get("/api/salao")
    assert response.status_code == 200
    body = response.json()
    assert body["salao"]["id"] == 1
    assert body["salao"]["nome"] == "Studio Belle & Co."
    assert len(body["horarios_funcionamento"]) == 7


def test_isolamento_saas_rejeita_salao_id_no_payload(client: TestClient) -> None:
    """Garante que o frontend não consegue forjar salao_id no corpo da requisição."""
    res_cliente = client.post(
        "/api/clientes",
        json={
            "salao_id": 2,
            "nome": "Tentativa Invasão Tenant",
            "telefone": "(11) 98888-7777",
        },
    )
    assert res_cliente.status_code == 422

    res_servico = client.post(
        "/api/servicos",
        json={
            "salao_id": 2,
            "nome": "Serviço Invasor",
            "duracao_minutos": 30,
            "preco": 50.0,
        },
    )
    assert res_servico.status_code == 422


def test_isolamento_saas_nao_lista_registros_de_outro_salao(client: TestClient) -> None:
    """O cliente #5 e o serviço #7 pertencem ao salão 2 e não devem ser acessíveis pelo salão 1."""
    res_cli = client.get("/api/clientes/5")
    assert res_cli.status_code == 404

    res_srv = client.get("/api/servicos/7")
    assert res_srv.status_code == 404

    res_ag = client.get("/api/agendamentos/6")
    assert res_ag.status_code == 404


def test_cors_restrito_por_variavel_ambiente(
    client: TestClient, monkeypatch
) -> None:
    """Verifica que CORS_ORIGINS é lido de variável de ambiente e nunca usa curinga '*' por padrão."""
    monkeypatch.setenv("CORS_ORIGINS", "http://127.0.0.1:8000,http://meusalao.local")
    res = client.get("/api/health")
    assert res.status_code == 200
    origins = res.json()["cors_origins"]
    assert "*" not in origins
    assert "http://127.0.0.1:8000" in origins
    assert "http://meusalao.local" in origins


def test_consistencia_scripts_sql_e_deploy() -> None:
    """Validações estruturais das correções nos scripts SQL, .env.example e deploy Ubuntu."""
    from backend.app.config import BASE_DIR

    # 1. FK composta de agendamentos -> usuarios sem ON DELETE SET NULL em coluna NOT NULL
    sql_tables = (BASE_DIR / "database" / "02_create_tables.sql").read_text(encoding="utf-8")
    assert "ON DELETE SET NULL" not in sql_tables
    assert "CONSTRAINT fk_agendamentos_usuario_salao FOREIGN KEY (usuario_id, salao_id)" in sql_tables
    assert "REFERENCES usuarios (id, salao_id) ON DELETE RESTRICT ON UPDATE CASCADE" in sql_tables

    # 2. Idempotência de 03_insert_data.sql (ON DUPLICATE KEY UPDATE nas 6 tabelas)
    sql_seed = (BASE_DIR / "database" / "03_insert_data.sql").read_text(encoding="utf-8")
    assert sql_seed.count("AS novo\nON DUPLICATE KEY UPDATE") == 6

    # 3. Alinhamento de .env.example com execução local (DB_ENGINE=sqlite) e CORS_ORIGINS
    env_example = (BASE_DIR / ".env.example").read_text(encoding="utf-8")
    assert "DB_ENGINE=sqlite" in env_example
    assert "CORS_ORIGINS=" in env_example

    # 4. Unidade systemd sem usuário 'ubuntu' fixo e script setup_ubuntu.sh coerente com APP_DIR
    systemd_unit = (BASE_DIR / "deploy" / "beautyschedule.service").read_text(encoding="utf-8")
    assert "User=__APP_USER__" in systemd_unit
    assert "Group=__APP_GROUP__" in systemd_unit
    assert "User=ubuntu" not in systemd_unit

    setup_sh = (BASE_DIR / "deploy" / "setup_ubuntu.sh").read_text(encoding="utf-8")
    assert 'cd "${APP_DIR}"' in setup_sh
    assert 'python3 -m venv "${APP_DIR}/.venv"' in setup_sh

