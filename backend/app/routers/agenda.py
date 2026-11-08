"""Rotas da API para consulta consolidada da Agenda diária."""

from __future__ import annotations

import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.services.agendamento_service import AgendamentoService

router = APIRouter(prefix="/api/agenda", tags=["Agenda"])


@router.get(
    "",
    summary="Consulta a agenda completa de uma data (expediente, agendamentos e grade de horários)",
)
def consultar_agenda_por_data(
    data: str | None = Query(
        default=None,
        description="Data no formato YYYY-MM-DD (padrão: data de hoje)",
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    data_alvo = data or datetime.date.today().isoformat()
    service = AgendamentoService(db)
    return service.consultar_agenda_dia(salao_id=tenant.salao_id, data_str=data_alvo)
