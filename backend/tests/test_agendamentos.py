"""Testes de criação, conflito de horários, expediente, reagendamento e cancelamento."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_criar_agendamento_valido(client: TestClient) -> None:
    # Segunda-feira 2026-11-09 às 16:00 (serviço 1 tem 60 min -> 16:00 às 17:00)
    res = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 1,
            "servico_id": 1,
            "data": "2026-11-09",
            "hora_inicio": "16:00",
            "canal_origem": "WHATSAPP",
            "observacoes": "Agendado via WhatsApp",
        },
    )
    assert res.status_code == 201
    ag = res.json()
    assert ag["hora_inicio"] == "16:00:00"
    assert ag["hora_fim"] == "17:00:00"
    assert ag["valor_cobrado"] == 120.00
    assert ag["status"] == "AGENDADO"


def test_impedir_conflito_de_horario_total_e_parcial(client: TestClient) -> None:
    # Em 2026-11-09 já existe o agendamento #1 das 09:00 às 10:00
    # 1) Tentativa no mesmo horário exato (09:00)
    res_exato = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 2,
            "servico_id": 1,
            "data": "2026-11-09",
            "hora_inicio": "09:00",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_exato.status_code == 409
    assert "Conflito de horário" in res_exato.json()["mensagem"]

    # 2) Tentativa com sobreposição parcial começando às 09:30 (terminaria às 10:15)
    res_parcial = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 3,
            "servico_id": 2,
            "data": "2026-11-09",
            "hora_inicio": "09:30",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_parcial.status_code == 409

    # 3) Tentativa começando antes (08:30) com duração de 60m (terminaria às 09:30 -> conflita com 09:00)
    res_antes = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 3,
            "servico_id": 1,
            "data": "2026-11-09",
            "hora_inicio": "08:30",
            "canal_origem": "PRESENCIAL",
        },
    )
    assert res_antes.status_code == 409


def test_validar_horario_de_funcionamento_do_salao(client: TestClient) -> None:
    # 1) Domingo (2026-11-08) -> Salão 1 é fechado aos domingos
    res_domingo = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 1,
            "servico_id": 1,
            "data": "2026-11-08",
            "hora_inicio": "10:00",
            "canal_origem": "WHATSAPP",
        },
    )
    assert res_domingo.status_code == 422
    assert "fechado" in res_domingo.json()["mensagem"].lower()

    # 2) Antes da abertura (07:30, sendo que abre às 08:00)
    res_cedo = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 1,
            "servico_id": 6,
            "data": "2026-11-09",
            "hora_inicio": "07:30",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_cedo.status_code == 422
    assert "fora do expediente" in res_cedo.json()["mensagem"].lower()

    # 3) Término após o fechamento (19:30 + 60 min = 20:30, mas fecha às 20:00)
    res_tarde = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 1,
            "servico_id": 1,
            "data": "2026-11-09",
            "hora_inicio": "19:30",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_tarde.status_code == 422
    assert "fora do expediente" in res_tarde.json()["mensagem"].lower()


def test_reagendar_e_cancelar_agendamento(client: TestClient) -> None:
    # Reagendar o agendamento #2 (2026-11-09 10:30) para um horário conflitante (09:00) deve falhar
    res_conflito = client.put(
        "/api/agendamentos/2/reagendar",
        json={
            "data": "2026-11-09",
            "hora_inicio": "09:00",
        },
    )
    assert res_conflito.status_code == 409

    # Reagendar #2 para um horário livre (12:00) deve funcionar
    res_ok = client.put(
        "/api/agendamentos/2/reagendar",
        json={
            "data": "2026-11-09",
            "hora_inicio": "12:00",
            "observacoes": "Reagendado a pedido da cliente",
        },
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["hora_inicio"] == "12:00:00"
    assert res_ok.json()["hora_fim"] == "12:45:00"

    # Cancelar o agendamento #1 (09:00 às 10:00)
    res_cancel = client.patch(
        "/api/agendamentos/1/cancelar",
        params={"motivo": "Imprevisto pessoal"},
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "CANCELADO"

    # Agora que o horário das 09:00 foi cancelado, outro agendamento pode usar as 09:00!
    res_novo_no_slot = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 3,
            "servico_id": 1,
            "data": "2026-11-09",
            "hora_inicio": "09:00",
            "canal_origem": "PRESENCIAL",
        },
    )
    assert res_novo_no_slot.status_code == 201


def test_impedir_agendamento_para_cliente_ou_servico_inativo(client: TestClient) -> None:
    # Cliente #4 está inativo no seed
    res_cli_inativo = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 4,
            "servico_id": 1,
            "data": "2026-11-11",
            "hora_inicio": "10:00",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_cli_inativo.status_code == 422

    # Inativar serviço #6 e tentar agendar
    client.patch("/api/servicos/6/inativar")
    res_srv_inativo = client.post(
        "/api/agendamentos",
        json={
            "cliente_id": 1,
            "servico_id": 6,
            "data": "2026-11-11",
            "hora_inicio": "10:00",
            "canal_origem": "TELEFONE",
        },
    )
    assert res_srv_inativo.status_code == 422
