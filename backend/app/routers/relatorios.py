"""Rotas da API para Relatórios operacionais e movimentação da agenda."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, Query

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.services.relatorio_service import RelatorioService

router = APIRouter(prefix="/api/relatorios", tags=["Relatórios"])


@router.get(
    "/resumo",
    summary="Retorna indicadores consolidados dos agendamentos, serviços e movimentação",
)
def obter_relatorio_resumo(
    data_inicio: str | None = Query(
        default=None, description="Data inicial YYYY-MM-DD opcional"
    ),
    data_fim: str | None = Query(
        default=None, description="Data final YYYY-MM-DD opcional"
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    service = RelatorioService(db)
    return service.gerar_relatorio_geral(
        salao_id=tenant.salao_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
