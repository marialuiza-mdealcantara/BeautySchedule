"""Rotas da API para gerenciamento de Clientes e consulta de histórico."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query, status

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.schemas import ClienteCreate, ClienteResponse, ClienteUpdate
from backend.app.services.cliente_service import ClienteService

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get(
    "",
    response_model=list[ClienteResponse],
    summary="Lista e filtra os clientes do salão",
)
def listar_clientes(
    apenas_ativos: bool | None = Query(
        default=None, description="Filtrar por clientes ativos (true) ou inativos (false)"
    ),
    busca: str | None = Query(
        default=None, description="Busca por nome, telefone ou e-mail"
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> list[dict[str, Any]]:
    service = ClienteService(db)
    return service.listar_clientes(
        salao_id=tenant.salao_id, apenas_ativos=apenas_ativos, busca=busca
    )


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Consulta os detalhes de um cliente específico",
)
def obter_cliente(
    cliente_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.obter_cliente(salao_id=tenant.salao_id, cliente_id=cliente_id)


@router.get(
    "/{cliente_id}/agendamentos",
    summary="Consulta o histórico completo de agendamentos de um cliente",
)
def consultar_historico_cliente(
    cliente_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.consultar_historico_agendamentos(
        salao_id=tenant.salao_id, cliente_id=cliente_id
    )


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastra um novo cliente no salão",
)
def cadastrar_cliente(
    payload: ClienteCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.cadastrar_cliente(salao_id=tenant.salao_id, payload=payload)


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Edita as informações de um cliente",
)
def editar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.atualizar_cliente(
        salao_id=tenant.salao_id, cliente_id=cliente_id, payload=payload
    )


@router.patch(
    "/{cliente_id}/inativar",
    response_model=ClienteResponse,
    summary="Inativa um cliente (exclusão lógica preservando histórico)",
)
def inativar_cliente(
    cliente_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.inativar_cliente(salao_id=tenant.salao_id, cliente_id=cliente_id)


@router.patch(
    "/{cliente_id}/reativar",
    response_model=ClienteResponse,
    summary="Reativa um cliente anteriormente inativado",
)
def reativar_cliente(
    cliente_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = ClienteService(db)
    return service.reativar_cliente(salao_id=tenant.salao_id, cliente_id=cliente_id)
