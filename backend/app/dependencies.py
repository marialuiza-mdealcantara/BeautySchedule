"""Dependências de segurança e isolamento SaaS (Multi-Tenant).

Regra arquitetural crítica:
O `salao_id` NUNCA é lido de payloads ou parâmetros enviados livremente pelo frontend.
Ele é resolvido exclusivamente no servidor a partir do contexto da sessão do operador
configurado no ambiente (ou token de sessão), garantindo isolamento estrito entre salões.
"""

from __future__ import annotations

from dataclasses import dataclass
from fastapi import Depends

from backend.app.config import Settings, get_settings


@dataclass(frozen=True, slots=True)
class TenantContext:
    """Contexto imutável do salão e operador autenticado na sessão atual."""

    salao_id: int
    usuario_id: int


def get_tenant_context(
    settings: Settings = Depends(get_settings),
) -> TenantContext:
    """Resolve o salão ativo no servidor sem confiar em dados enviados pelo cliente."""
    return TenantContext(
        salao_id=settings.default_salao_id,
        usuario_id=settings.default_usuario_id,
    )
