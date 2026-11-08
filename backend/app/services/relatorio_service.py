"""Regras de negócio para geração de Relatórios e indicadores da agenda."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from backend.app.database import DatabaseConnection
from backend.app.repositories.agendamento_repository import AgendamentoRepository
from backend.app.repositories.cliente_repository import ClienteRepository
from backend.app.repositories.servico_repository import ServicoRepository


class RelatorioService:
    """Serviço consolidador de indicadores operacionais e relatórios do salão."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.agendamento_repo = AgendamentoRepository(db)
        self.cliente_repo = ClienteRepository(db)
        self.servico_repo = ServicoRepository(db)

    def gerar_relatorio_geral(
        self,
        salao_id: int,
        data_inicio: str | None = None,
        data_fim: str | None = None,
    ) -> dict[str, Any]:
        agendamentos = self.agendamento_repo.list_agendamentos(
            salao_id=salao_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
        clientes = self.cliente_repo.list_clientes(salao_id=salao_id)
        servicos = self.servico_repo.list_servicos(salao_id=salao_id)

        por_status = {
            "AGENDADO": 0,
            "CONFIRMADO": 0,
            "CONCLUIDO": 0,
            "CANCELADO": 0,
        }
        por_canal: dict[str, int] = defaultdict(int)
        servicos_stats: dict[int, dict[str, Any]] = {}
        movimentacao_por_data: dict[str, dict[str, Any]] = {}

        faturamento_realizado = 0.0
        faturamento_previsto = 0.0

        for ag in agendamentos:
            st = ag["status"]
            por_status[st] = por_status.get(st, 0) + 1
            por_canal[ag["canal_origem"]] += 1

            valor = float(ag["valor_cobrado"])
            if st == "CONCLUIDO":
                faturamento_realizado += valor
                faturamento_previsto += valor
            elif st in ("AGENDADO", "CONFIRMADO"):
                faturamento_previsto += valor

            # Estatísticas por serviço (considerando agendamentos não cancelados)
            srv_id = int(ag["servico_id"])
            if srv_id not in servicos_stats:
                servicos_stats[srv_id] = {
                    "servico_id": srv_id,
                    "servico_nome": ag["servico_nome"],
                    "duracao_minutos": ag["servico_duracao_minutos"],
                    "total_agendamentos": 0,
                    "ativos_ou_concluidos": 0,
                    "cancelados": 0,
                    "receita_gerada": 0.0,
                }
            servicos_stats[srv_id]["total_agendamentos"] += 1
            if st == "CANCELADO":
                servicos_stats[srv_id]["cancelados"] += 1
            else:
                servicos_stats[srv_id]["ativos_ou_concluidos"] += 1
                servicos_stats[srv_id]["receita_gerada"] = round(
                    servicos_stats[srv_id]["receita_gerada"] + valor, 2
                )

            # Movimentação diária
            dt = ag["data"]
            if dt not in movimentacao_por_data:
                movimentacao_por_data[dt] = {
                    "data": dt,
                    "total": 0,
                    "ativos": 0,
                    "concluidos": 0,
                    "cancelados": 0,
                    "receita_prevista": 0.0,
                }
            movimentacao_por_data[dt]["total"] += 1
            if st == "CANCELADO":
                movimentacao_por_data[dt]["cancelados"] += 1
            else:
                movimentacao_por_data[dt]["ativos"] += 1
                movimentacao_por_data[dt]["receita_prevista"] = round(
                    movimentacao_por_data[dt]["receita_prevista"] + valor, 2
                )
            if st == "CONCLUIDO":
                movimentacao_por_data[dt]["concluidos"] += 1

        total_agendamentos = len(agendamentos)
        taxa_cancelamento = (
            round((por_status["CANCELADO"] / total_agendamentos) * 100, 1)
            if total_agendamentos > 0
            else 0.0
        )

        ranking_servicos = sorted(
            servicos_stats.values(),
            key=lambda x: (x["ativos_ou_concluidos"], x["receita_gerada"]),
            reverse=True,
        )

        movimentacao_diaria = sorted(
            movimentacao_por_data.values(),
            key=lambda x: x["data"],
        )

        return {
            "periodo": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
            },
            "indicadores": {
                "total_clientes": len(clientes),
                "clientes_ativos": sum(1 for c in clientes if c["ativo"]),
                "clientes_inativos": sum(1 for c in clientes if not c["ativo"]),
                "total_servicos": len(servicos),
                "servicos_ativos": sum(1 for s in servicos if s["ativo"]),
                "total_agendamentos": total_agendamentos,
                "agendamentos_ativos": (
                    por_status["AGENDADO"]
                    + por_status["CONFIRMADO"]
                    + por_status["CONCLUIDO"]
                ),
                "taxa_cancelamento_percentual": taxa_cancelamento,
                "faturamento_realizado": round(faturamento_realizado, 2),
                "faturamento_previsto": round(faturamento_previsto, 2),
            },
            "por_status": por_status,
            "por_canal_origem": dict(por_canal),
            "desempenho_servicos": ranking_servicos,
            "movimentacao_diaria": movimentacao_diaria,
            "agendamentos_recentes": agendamentos[-15:],
        }
