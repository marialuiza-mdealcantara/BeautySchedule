"""Regras de negócio para gerenciamento de Clientes."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection
from backend.app.exceptions import BusinessRuleError, NotFoundError
from backend.app.repositories.agendamento_repository import AgendamentoRepository
from backend.app.repositories.cliente_repository import ClienteRepository
from backend.app.schemas import ClienteCreate, ClienteUpdate


class ClienteService:
    """Serviço de domínio responsável pelas operações de clientes de um salão."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.repo = ClienteRepository(db)
        self.agendamento_repo = AgendamentoRepository(db)

    def listar_clientes(
        self,
        salao_id: int,
        apenas_ativos: bool | None = None,
        busca: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.repo.list_clientes(
            salao_id=salao_id, apenas_ativos=apenas_ativos, busca=busca
        )

    def obter_cliente(self, salao_id: int, cliente_id: int) -> dict[str, Any]:
        cliente = self.repo.get_by_id(salao_id, cliente_id)
        if not cliente:
            raise NotFoundError(f"Cliente #{cliente_id} não encontrado neste salão.")
        return cliente

    def cadastrar_cliente(
        self, salao_id: int, payload: ClienteCreate
    ) -> dict[str, Any]:
        return self.repo.create(
            salao_id=salao_id,
            nome=payload.nome,
            telefone=payload.telefone,
            email=payload.email,
            observacoes=payload.observacoes,
        )

    def atualizar_cliente(
        self, salao_id: int, cliente_id: int, payload: ClienteUpdate
    ) -> dict[str, Any]:
        atual = self.obter_cliente(salao_id, cliente_id)

        novo_nome = payload.nome if payload.nome is not None else atual["nome"]
        novo_telefone = (
            payload.telefone if payload.telefone is not None else atual["telefone"]
        )
        novo_email = (
            payload.email
            if "email" in payload.model_fields_set
            else atual["email"]
        )
        novas_obs = (
            payload.observacoes
            if "observacoes" in payload.model_fields_set
            else atual["observacoes"]
        )
        novo_ativo = payload.ativo if payload.ativo is not None else bool(atual["ativo"])

        atualizado = self.repo.update(
            salao_id=salao_id,
            cliente_id=cliente_id,
            nome=novo_nome,
            telefone=novo_telefone,
            email=novo_email,
            observacoes=novas_obs,
            ativo=novo_ativo,
        )
        assert atualizado is not None
        return atualizado

    def inativar_cliente(self, salao_id: int, cliente_id: int) -> dict[str, Any]:
        atual = self.obter_cliente(salao_id, cliente_id)
        if not atual["ativo"]:
            raise BusinessRuleError("Este cliente já se encontra inativo.")
        inativado = self.repo.set_ativo(salao_id, cliente_id, ativo=False)
        assert inativado is not None
        return inativado

    def reativar_cliente(self, salao_id: int, cliente_id: int) -> dict[str, Any]:
        self.obter_cliente(salao_id, cliente_id)
        reativado = self.repo.set_ativo(salao_id, cliente_id, ativo=True)
        assert reativado is not None
        return reativado

    def consultar_historico_agendamentos(
        self, salao_id: int, cliente_id: int
    ) -> dict[str, Any]:
        cliente = self.obter_cliente(salao_id, cliente_id)
        historico = self.agendamento_repo.list_agendamentos(
            salao_id=salao_id, cliente_id=cliente_id
        )
        return {
            "cliente": cliente,
            "total_agendamentos": len(historico),
            "agendamentos": historico,
        }
