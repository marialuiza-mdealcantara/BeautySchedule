"""Testes automatizados para cadastro, consulta, edição, inativação e validações de Serviços."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_cadastrar_e_consultar_servico(client: TestClient) -> None:
    payload = {
        "nome": "Maquiagem Social Completa",
        "descricao": "Preparação de pele blindada e aplicação de cílios.",
        "duracao_minutos": 75,
        "preco": 195.50,
    }
    res_post = client.post("/api/servicos", json=payload)
    assert res_post.status_code == 201
    criado = res_post.json()
    assert criado["id"] > 0
    assert criado["salao_id"] == 1
    assert criado["duracao_minutos"] == 75
    assert criado["preco"] == 195.50
    assert criado["ativo"] is True

    res_get = client.get(f"/api/servicos/{criado['id']}")
    assert res_get.status_code == 200
    assert res_get.json()["nome"] == "Maquiagem Social Completa"


def test_impedir_servico_duplicado_no_mesmo_salao(client: TestClient) -> None:
    res = client.post(
        "/api/servicos",
        json={
            "nome": "Escova Modelada",
            "duracao_minutos": 45,
            "preco": 80.0,
        },
    )
    assert res.status_code == 409


def test_editar_inativar_e_reativar_servico(client: TestClient) -> None:
    res_put = client.put(
        "/api/servicos/2",
        json={
            "preco": 85.00,
            "duracao_minutos": 50,
        },
    )
    assert res_put.status_code == 200
    assert res_put.json()["preco"] == 85.00
    assert res_put.json()["duracao_minutos"] == 50

    res_inativar = client.patch("/api/servicos/2/inativar")
    assert res_inativar.status_code == 200
    assert res_inativar.json()["ativo"] is False

    res_reativar = client.patch("/api/servicos/2/reativar")
    assert res_reativar.status_code == 200
    assert res_reativar.json()["ativo"] is True


def test_validacoes_duracao_e_preco_servico(client: TestClient) -> None:
    res_duracao_zero = client.post(
        "/api/servicos",
        json={"nome": "Serviço Inválido", "duracao_minutos": 0, "preco": 50.0},
    )
    assert res_duracao_zero.status_code == 422

    res_preco_negativo = client.post(
        "/api/servicos",
        json={"nome": "Serviço Inválido", "duracao_minutos": 30, "preco": -10.0},
    )
    assert res_preco_negativo.status_code == 422
