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
