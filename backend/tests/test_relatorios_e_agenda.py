"""Testes para consulta de Agenda por data e Relatórios operacionais."""

from __future__ import annotations

from fastapi.testclient import TestClient


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
