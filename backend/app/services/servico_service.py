"""Regras de negócio para gerenciamento do catálogo de Serviços do salão."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection
from backend.app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from backend.app.repositories.servico_repository import ServicoRepository
from backend.app.schemas import ServicoCreate, ServicoUpdate


class ServicoService:
    """Serviço de domínio responsável pelas operações de serviços."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.repo = ServicoRepository(db)

    def listar_servicos(
        self,
        salao_id: int,
        apenas_ativos: bool | None = None,
        busca: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.repo.list_servicos(
            salao_id=salao_id, apenas_ativos=apenas_ativos, busca=busca
        )

    def obter_servico(self, salao_id: int, servico_id: int) -> dict[str, Any]:
        servico = self.repo.get_by_id(salao_id, servico_id)
        if not servico:
            raise NotFoundError(f"Serviço #{servico_id} não encontrado neste salão.")
        return servico

    def cadastrar_servico(
        self, salao_id: int, payload: ServicoCreate
    ) -> dict[str, Any]:
        existente = self.repo.get_by_nome(salao_id, payload.nome)
        if existente:
            raise ConflictError(
                f"Já existe um serviço cadastrado com o nome '{payload.nome}' neste salão."
            )
        return self.repo.create(
            salao_id=salao_id,
            nome=payload.nome,
            descricao=payload.descricao,
            duracao_minutos=payload.duracao_minutos,
            preco=payload.preco,
        )

    def atualizar_servico(
        self, salao_id: int, servico_id: int, payload: ServicoUpdate
    ) -> dict[str, Any]:
        atual = self.obter_servico(salao_id, servico_id)

        novo_nome = payload.nome if payload.nome is not None else atual["nome"]
        if novo_nome.lower() != atual["nome"].lower():
            conflito = self.repo.get_by_nome(salao_id, novo_nome)
            if conflito and conflito["id"] != servico_id:
                raise ConflictError(
                    f"Já existe outro serviço cadastrado com o nome '{novo_nome}'."
                )

        nova_descricao = (
            payload.descricao
            if "descricao" in payload.model_fields_set
            else atual["descricao"]
        )
        nova_duracao = (
            payload.duracao_minutos
            if payload.duracao_minutos is not None
            else atual["duracao_minutos"]
        )
        novo_preco = payload.preco if payload.preco is not None else atual["preco"]
        novo_ativo = payload.ativo if payload.ativo is not None else bool(atual["ativo"])

        atualizado = self.repo.update(
            salao_id=salao_id,
            servico_id=servico_id,
            nome=novo_nome,
            descricao=nova_descricao,
            duracao_minutos=nova_duracao,
            preco=novo_preco,
            ativo=novo_ativo,
        )
        assert atualizado is not None
        return atualizado

    def inativar_servico(self, salao_id: int, servico_id: int) -> dict[str, Any]:
        atual = self.obter_servico(salao_id, servico_id)
        if not atual["ativo"]:
            raise BusinessRuleError("Este serviço já se encontra inativo.")
        inativado = self.repo.set_ativo(salao_id, servico_id, ativo=False)
        assert inativado is not None
        return inativado

    def reativar_servico(self, salao_id: int, servico_id: int) -> dict[str, Any]:
        self.obter_servico(salao_id, servico_id)
        reativado = self.repo.set_ativo(salao_id, servico_id, ativo=True)
        assert reativado is not None
        return reativado
