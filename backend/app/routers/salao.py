"""Rotas para consulta de informações do Salão atual e Horários de Funcionamento."""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends

from backend.app.database import DatabaseConnection, get_db
from backend.app.dependencies import TenantContext, get_tenant_context
from backend.app.exceptions import NotFoundError
from backend.app.repositories.salao_repository import SalaoRepository

router = APIRouter(prefix="/api/salao", tags=["Salão e Expediente"])


@router.get("", summary="Obtém os dados do salão (tenant) ativo na sessão")
def obter_salao_atual(
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> dict[str, Any]:
    repo = SalaoRepository(db)
    salao = repo.get_salao_by_id(tenant.salao_id)
    if not salao:
        raise NotFoundError("Salão ativo não encontrado.")
    operador = repo.get_usuario_by_id(tenant.salao_id, tenant.usuario_id)
    horarios = repo.list_horarios_funcionamento(tenant.salao_id)
    return {
        "salao": salao,
        "operador": operador,
        "horarios_funcionamento": horarios,
    }


@router.get("/horarios", summary="Lista os horários de funcionamento do salão")
def listar_horarios_funcionamento(
    tenant: TenantContext = Depends(get_tenant_context),
    db: DatabaseConnection = Depends(get_db),
) -> list[dict[str, Any]]:
    repo = SalaoRepository(db)
    return repo.list_horarios_funcionamento(tenant.salao_id)
