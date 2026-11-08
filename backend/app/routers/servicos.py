"""Rotas da API para gerenciamento de Serviços do salão."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query, status

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.schemas import ServicoCreate, ServicoResponse, ServicoUpdate
from backend.app.services.servico_service import ServicoService

router = APIRouter(prefix="/api/servicos", tags=["Serviços"])


@router.get(
    "",
    response_model=list[ServicoResponse],
    summary="Lista os serviços cadastrados no salão",
)
def listar_servicos(
    apenas_ativos: bool | None = Query(
        default=None, description="Filtrar por serviços ativos (true) ou inativos (false)"
    ),
    busca: str | None = Query(
        default=None, description="Busca por nome ou descrição do serviço"
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> list[dict[str, Any]]:
    service = ServicoService(db)
    return service.listar_servicos(
        salao_id=tenant.salao_id, apenas_ativos=apenas_ativos, busca=busca
    )


@router.get(
    "/{servico_id}",
    response_model=ServicoResponse,
    summary="Consulta detalhes de um serviço específico",
)
def obter_servico(
    servico_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ServicoService(db)
    return service.obter_servico(salao_id=tenant.salao_id, servico_id=servico_id)


@router.post(
    "",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo serviço informando duração e preço",
)
def cadastrar_servico(
    payload: ServicoCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ServicoService(db)
    return service.cadastrar_servico(salao_id=tenant.salao_id, payload=payload)


@router.put(
    "/{servico_id}",
    response_model=ServicoResponse,
    summary="Edita informações, duração ou preço de um serviço",
)
def editar_servico(
    servico_id: int,
    payload: ServicoUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ServicoService(db)
    return service.atualizar_servico(
        salao_id=tenant.salao_id, servico_id=servico_id, payload=payload
    )


@router.patch(
    "/{servico_id}/inativar",
    response_model=ServicoResponse,
    summary="Inativa um serviço do catálogo",
)
def inativar_servico(
    servico_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ServicoService(db)
    return service.inativar_servico(salao_id=tenant.salao_id, servico_id=servico_id)


@router.patch(
    "/{servico_id}/reativar",
    response_model=ServicoResponse,
    summary="Reativa um serviço anteriormente inativado",
)
def reativar_servico(
    servico_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ServicoService(db)
    return service.reativar_servico(salao_id=tenant.salao_id, servico_id=servico_id)
