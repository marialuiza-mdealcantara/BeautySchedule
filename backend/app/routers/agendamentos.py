"""Rotas da API para criação, consulta, reagendamento e cancelamento de Agendamentos."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query, status

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.schemas import (
    AgendamentoCreate,
    AgendamentoReagendar,
    AgendamentoResponse,
    AgendamentoStatusUpdate,
)
from backend.app.services.agendamento_service import AgendamentoService

router = APIRouter(prefix="/api/agendamentos", tags=["Agendamentos"])


@router.get(
    "",
    response_model=list[AgendamentoResponse],
    summary="Consulta agendamentos com filtros por data, período, cliente, serviço e status",
)
def listar_agendamentos(
    data: str | None = Query(default=None, description="Data exata YYYY-MM-DD"),
    data_inicio: str | None = Query(default=None, description="Data inicial YYYY-MM-DD"),
    data_fim: str | None = Query(default=None, description="Data final YYYY-MM-DD"),
    cliente_id: int | None = Query(default=None, description="ID do cliente"),
    servico_id: int | None = Query(default=None, description="ID do serviço"),
    status_filtro: str | None = Query(
        default=None, alias="status", description="Status (AGENDADO, CONFIRMADO, CONCLUIDO, CANCELADO)"
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> list[dict[str, Any]]:
    service = AgendamentoService(db)
    return service.listar_agendamentos(
        salao_id=tenant.salao_id,
        data=data,
        data_inicio=data_inicio,
        data_fim=data_fim,
        cliente_id=cliente_id,
        servico_id=servico_id,
        status=status_filtro,
    )


@router.get(
    "/{agendamento_id}",
    response_model=AgendamentoResponse,
    summary="Obtém os detalhes de um agendamento específico",
)
def obter_agendamento(
    agendamento_id: int,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = AgendamentoService(db)
    return service.obter_agendamento(
        salao_id=tenant.salao_id, agendamento_id=agendamento_id
    )


@router.post(
    "",
    response_model=AgendamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um novo agendamento validando expediente e conflitos de horário",
)
def criar_agendamento(
    payload: AgendamentoCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = AgendamentoService(db)
    return service.criar_agendamento(
        salao_id=tenant.salao_id,
        usuario_id=tenant.usuario_id,
        payload=payload,
    )


@router.put(
    "/{agendamento_id}/reagendar",
    response_model=AgendamentoResponse,
    summary="Reagenda data/horário (e opcionalmente serviço) validando disponibilidade",
)
def reagendar_agendamento(
    agendamento_id: int,
    payload: AgendamentoReagendar,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = AgendamentoService(db)
    return service.reagendar(
        salao_id=tenant.salao_id,
        agendamento_id=agendamento_id,
        payload=payload,
    )


@router.patch(
    "/{agendamento_id}/cancelar",
    response_model=AgendamentoResponse,
    summary="Cancela um agendamento liberando o horário na agenda",
)
def cancelar_agendamento(
    agendamento_id: int,
    motivo: str | None = Query(default=None, description="Motivo opcional do cancelamento"),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = AgendamentoService(db)
    return service.cancelar(
        salao_id=tenant.salao_id,
        agendamento_id=agendamento_id,
        motivo=motivo,
    )


@router.patch(
    "/{agendamento_id}/status",
    response_model=AgendamentoResponse,
    summary="Atualiza o status do agendamento (CONFIRMADO, CONCLUIDO, CANCELADO)",
)
def atualizar_status_agendamento(
    agendamento_id: int,
    payload: AgendamentoStatusUpdate,
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = AgendamentoService(db)
    return service.atualizar_status(
        salao_id=tenant.salao_id,
        agendamento_id=agendamento_id,
        payload=payload,
    )
