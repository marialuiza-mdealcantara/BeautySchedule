"""Testes automatizados para cadastro, consulta, edição, inativação e validações de Clientes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_cadastrar_e_consultar_cliente(client: TestClient) -> None:
    payload = {
        "nome": "Beatriz Helena Nogueira",
        "telefone": "(11) 97777-8899",
        "email": "beatriz.nogueira@email.com",
        "observacoes": "Prefere atendimento às sextas-feiras.",
    }
    res_post = client.post("/api/clientes", json=payload)
    assert res_post.status_code == 201
    criado = res_post.json()
    assert criado["id"] > 0
    assert criado["salao_id"] == 1
    assert criado["nome"] == payload["nome"]
    assert criado["ativo"] is True

    res_get = client.get(f"/api/clientes/{criado['id']}")
    assert res_get.status_code == 200
    assert res_get.json()["email"] == "beatriz.nogueira@email.com"


def test_listar_e_filtrar_clientes(client: TestClient) -> None:
    res_todos = client.get("/api/clientes")
    assert res_todos.status_code == 200
    assert len(res_todos.json()) == 4  # 4 clientes no salão 1

    res_ativos = client.get("/api/clientes", params={"apenas_ativos": "true"})
    assert res_ativos.status_code == 200
    assert len(res_ativos.json()) == 3

    res_busca = client.get("/api/clientes", params={"busca": "Mariana"})
    assert res_busca.status_code == 200
    assert len(res_busca.json()) == 1
    assert res_busca.json()[0]["nome"] == "Mariana Costa Oliveira"


def test_editar_inativar_e_reativar_cliente(client: TestClient) -> None:
    res_put = client.put(
        "/api/clientes/1",
        json={
            "nome": "Ana Beatriz Silva Atualizada",
            "telefone": "(11) 99111-9999",
        },
    )
    assert res_put.status_code == 200
    assert res_put.json()["nome"] == "Ana Beatriz Silva Atualizada"
    assert res_put.json()["telefone"] == "(11) 99111-9999"

    # Inativar
    res_inativar = client.patch("/api/clientes/1/inativar")
    assert res_inativar.status_code == 200
    assert res_inativar.json()["ativo"] is False

    # Inativar novamente deve retornar erro de regra de negócio (422)
    res_inativar_duplo = client.patch("/api/clientes/1/inativar")
    assert res_inativar_duplo.status_code == 422

    # Reativar
    res_reativar = client.patch("/api/clientes/1/reativar")
    assert res_reativar.status_code == 200
    assert res_reativar.json()["ativo"] is True


def test_consultar_historico_agendamentos_por_cliente(client: TestClient) -> None:
    res = client.get("/api/clientes/1/agendamentos")
    assert res.status_code == 200
    dados = res.json()
    assert dados["cliente"]["id"] == 1
    assert dados["total_agendamentos"] == 2
    assert len(dados["agendamentos"]) == 2


def test_validacoes_dados_cliente(client: TestClient) -> None:
    # Telefone curto inválido
    res_tel = client.post(
        "/api/clientes",
        json={"nome": "Cliente Teste", "telefone": "1234"},
    )
    assert res_tel.status_code == 422

    # E-mail inválido
    res_email = client.post(
        "/api/clientes",
        json={
            "nome": "Cliente Teste",
            "telefone": "(11) 98888-7777",
            "email": "email-invalido",
        },
    )
    assert res_email.status_code == 422
