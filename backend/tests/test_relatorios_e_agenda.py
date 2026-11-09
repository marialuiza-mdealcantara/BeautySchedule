"""Testes para consulta de Agenda por data, Relatórios e carregamento concorrente do Dashboard."""

from __future__ import annotations

import concurrent.futures
import sqlite3
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.database import init_sqlite_db
from backend.app.main import app


def test_consultar_agenda_por_data(client: TestClient) -> None:
    res = client.get("/api/agenda", params={"data": "2026-11-09"})
    assert res.status_code == 200
    agenda = res.json()
    assert agenda["data"] == "2026-11-09"
    assert agenda["expediente"]["aberto"] is True
    assert agenda["resumo"]["total_dia"] == 3
    assert agenda["resumo"]["ativos"] == 3
    assert len(agenda["grade_horarios"]) == 24  # 08:00 às 20:00 em blocos de 30m

    # Verificar que o slot das 09:00 consta como ocupado
    slot_09 = next(s for s in agenda["grade_horarios"] if s["horario"] == "09:00")
    assert slot_09["disponivel"] is False
    assert slot_09["cliente_nome"] == "Ana Beatriz Silva"


def test_relatorio_resumo_geral(client: TestClient) -> None:
    res = client.get("/api/relatorios/resumo")
    assert res.status_code == 200
    rel = res.json()
    ind = rel["indicadores"]

    assert ind["total_clientes"] == 4
    assert ind["clientes_ativos"] == 3
    assert ind["total_servicos"] == 6
    assert ind["total_agendamentos"] == 5  # 5 agendamentos do salão 1
    assert ind["agendamentos_ativos"] == 4  # 1 cancelado
    assert ind["faturamento_realizado"] == 85.00  # Agendamento #3 concluído
    assert ind["faturamento_previsto"] == 420.00  # 120 + 75 + 85 + 140
    assert len(rel["desempenho_servicos"]) > 0
    assert len(rel["movimentacao_diaria"]) == 2


def test_carregamento_concorrente_dashboard(client: TestClient) -> None:
    """Reproduz as chamadas paralelas do Dashboard (GET /api/salao e GET /api/relatorios/resumo)
    garantindo que não ocorra sqlite3.ProgrammingError entre threads do threadpool.
    """
    endpoints = [
        "/api/salao",
        "/api/relatorios/resumo",
        "/api/agenda?data=2026-11-09",
        "/api/clientes",
        "/api/servicos",
        "/api/agendamentos",
    ]

    def call_endpoint(ep: str) -> tuple[str, int]:
        resp = client.get(ep)
        return ep, resp.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        for _ in range(5):
            futures = [executor.submit(call_endpoint, ep) for ep in endpoints]
            results = [f.result() for f in futures]
            for ep, status_code in results:
                assert status_code == 200, f"Falha concorrente em {ep}: HTTP {status_code}"


def test_dashboard_cenario_sem_registros(tmp_path: Path, monkeypatch) -> None:
    """Testa o carregamento do Dashboard quando o salão não possui clientes, serviços ou agendamentos."""
    empty_db = tmp_path / "empty_salon.db"
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(empty_db))
    monkeypatch.setenv("DEFAULT_SALAO_ID", "1")
    monkeypatch.setenv("DEFAULT_USUARIO_ID", "1")

    init_sqlite_db(str(empty_db), seed=False)
    conn = sqlite3.connect(str(empty_db))
    conn.execute(
        "INSERT INTO saloes (id, nome, telefone, ativo) VALUES (1, 'Salão Vazio', '(11) 90000-0000', 1)"
    )
    conn.commit()
    conn.close()

    with TestClient(app) as tc:
        res_salao = tc.get("/api/salao")
        assert res_salao.status_code == 200
        assert res_salao.json()["salao"]["nome"] == "Salão Vazio"
        assert res_salao.json()["horarios_funcionamento"] == []

        res_rel = tc.get("/api/relatorios/resumo")
        assert res_rel.status_code == 200
        rel = res_rel.json()
        assert rel["indicadores"]["total_agendamentos"] == 0
        assert rel["indicadores"]["agendamentos_ativos"] == 0
        assert rel["indicadores"]["clientes_ativos"] == 0
        assert rel["indicadores"]["servicos_ativos"] == 0
        assert rel["indicadores"]["faturamento_previsto"] == 0.0
        assert rel["agendamentos_recentes"] == []


def test_tratamento_erro_camada_dados(client: TestClient, monkeypatch) -> None:
    """Garante que falhas de banco de dados retornem JSON estruturado (HTTP 500) em vez de texto puro."""
    from backend.app.repositories.salao_repository import SalaoRepository

    def broken_query(*_args, **_kwargs):
        raise sqlite3.OperationalError("Simulacao de falha de banco")

    monkeypatch.setattr(SalaoRepository, "get_salao_by_id", broken_query)
    res = client.get("/api/salao")
    assert res.status_code == 500
    body = res.json()
    assert body["erro"] is True
    assert "banco de dados" in body["mensagem"].lower()

