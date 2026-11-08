"""Regras de negócio para Agendamentos, validação de expediente e prevenção de conflitos."""

from __future__ import annotations

import datetime
from typing import Any

from backend.app.database import DatabaseConnection
from backend.app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from backend.app.repositories.agendamento_repository import AgendamentoRepository
from backend.app.repositories.cliente_repository import ClienteRepository
from backend.app.repositories.salao_repository import SalaoRepository
from backend.app.repositories.servico_repository import ServicoRepository
from backend.app.schemas import (
    AgendamentoCreate,
    AgendamentoReagendar,
    AgendamentoStatusUpdate,
)


def _calcular_hora_fim(hora_inicio_str: str, duracao_minutos: int) -> str:
    """Calcula o horário final do atendimento somando a duração do serviço."""
    hora_obj = datetime.time.fromisoformat(hora_inicio_str)
    dt_inicio = datetime.datetime.combine(datetime.date(2000, 1, 1), hora_obj)
    dt_fim = dt_inicio + datetime.timedelta(minutes=duracao_minutos)
    if dt_fim.date() > dt_inicio.date():
        raise BusinessRuleError(
            "O horário de término do serviço ultrapassa o final do dia (23:59)."
        )
    return dt_fim.time().strftime("%H:%M:%S")


class AgendamentoService:
    """Serviço de domínio para gestão completa de agendamentos e agenda diária."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.repo = AgendamentoRepository(db)
        self.cliente_repo = ClienteRepository(db)
        self.servico_repo = ServicoRepository(db)
        self.salao_repo = SalaoRepository(db)

    def _validar_horario_funcionamento(
        self, salao_id: int, data_str: str, hora_inicio: str, hora_fim: str
    ) -> None:
        data_obj = datetime.date.fromisoformat(data_str)
        dia_semana = data_obj.weekday()  # 0 = Segunda-feira ... 6 = Domingo
        expediente = self.salao_repo.get_horario_por_dia_semana(salao_id, dia_semana)

        if not expediente or not expediente["aberto"]:
            dia_nome = expediente["dia_nome"] if expediente else "neste dia da semana"
            raise BusinessRuleError(
                f"O salão está fechado ({dia_nome}). Não é possível agendar nesta data."
            )

        abertura = str(expediente["hora_abertura"])
        fechamento = str(expediente["hora_fechamento"])

        if hora_inicio < abertura or hora_fim > fechamento:
            raise BusinessRuleError(
                f"Horário fora do expediente do salão ({abertura[:5]} às {fechamento[:5]}). "
                f"O atendimento solicitado iria das {hora_inicio[:5]} às {hora_fim[:5]}."
            )

    def _validar_conflito_agenda(
        self,
        salao_id: int,
        data_str: str,
        hora_inicio: str,
        hora_fim: str,
        exclude_agendamento_id: int | None = None,
    ) -> None:
        conflitos = self.repo.find_conflicting_agendamentos(
            salao_id=salao_id,
            data=data_str,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            exclude_agendamento_id=exclude_agendamento_id,
        )
        if conflitos:
            primeiro = conflitos[0]
            raise ConflictError(
                f"Conflito de horário: já existe o agendamento #{primeiro['id']} "
                f"({primeiro['cliente_nome']} - {primeiro['servico_nome']}) "
                f"das {primeiro['hora_inicio'][:5]} às {primeiro['hora_fim'][:5]} nesta data."
            )

    def listar_agendamentos(
        self,
        salao_id: int,
        data: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        cliente_id: int | None = None,
        servico_id: int | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.repo.list_agendamentos(
            salao_id=salao_id,
            data=data,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cliente_id=cliente_id,
            servico_id=servico_id,
            status=status,
        )

    def obter_agendamento(
        self, salao_id: int, agendamento_id: int
    ) -> dict[str, Any]:
        agendamento = self.repo.get_by_id(salao_id, agendamento_id)
        if not agendamento:
            raise NotFoundError(
                f"Agendamento #{agendamento_id} não encontrado neste salão."
            )
        return agendamento

    def criar_agendamento(
        self,
        salao_id: int,
        usuario_id: int | None,
        payload: AgendamentoCreate,
    ) -> dict[str, Any]:
        cliente = self.cliente_repo.get_by_id(salao_id, payload.cliente_id)
        if not cliente:
            raise NotFoundError(
                f"Cliente #{payload.cliente_id} não encontrado neste salão."
            )
        if not cliente["ativo"]:
            raise BusinessRuleError(
                f"O cliente '{cliente['nome']}' está inativo e não pode receber novos agendamentos."
            )

        servico = self.servico_repo.get_by_id(salao_id, payload.servico_id)
        if not servico:
            raise NotFoundError(
                f"Serviço #{payload.servico_id} não encontrado neste salão."
            )
        if not servico["ativo"]:
            raise BusinessRuleError(
                f"O serviço '{servico['nome']}' está inativo e não pode ser agendado."
            )

        hora_fim = _calcular_hora_fim(
            payload.hora_inicio, int(servico["duracao_minutos"])
        )

        self._validar_horario_funcionamento(
            salao_id=salao_id,
            data_str=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
        )
        self._validar_conflito_agenda(
            salao_id=salao_id,
            data_str=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
        )

        return self.repo.create(
            salao_id=salao_id,
            cliente_id=payload.cliente_id,
            servico_id=payload.servico_id,
            usuario_id=usuario_id,
            data=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
            canal_origem=payload.canal_origem,
            observacoes=payload.observacoes,
            valor_cobrado=float(servico["preco"]),
        )

    def reagendar(
        self,
        salao_id: int,
        agendamento_id: int,
        payload: AgendamentoReagendar,
    ) -> dict[str, Any]:
        atual = self.obter_agendamento(salao_id, agendamento_id)
        if atual["status"] == "CANCELADO":
            raise BusinessRuleError(
                "Não é possível reagendar um agendamento já cancelado."
            )
        if atual["status"] == "CONCLUIDO":
            raise BusinessRuleError(
                "Não é possível reagendar um atendimento já concluído."
            )

        servico_id = (
            payload.servico_id
            if payload.servico_id is not None
            else int(atual["servico_id"])
        )
        servico = self.servico_repo.get_by_id(salao_id, servico_id)
        if not servico:
            raise NotFoundError(f"Serviço #{servico_id} não encontrado neste salão.")
        if not servico["ativo"]:
            raise BusinessRuleError(
                f"O serviço '{servico['nome']}' está inativo e não pode ser utilizado no reagendamento."
            )

        hora_fim = _calcular_hora_fim(
            payload.hora_inicio, int(servico["duracao_minutos"])
        )

        self._validar_horario_funcionamento(
            salao_id=salao_id,
            data_str=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
        )
        self._validar_conflito_agenda(
            salao_id=salao_id,
            data_str=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
            exclude_agendamento_id=agendamento_id,
        )

        novas_obs = (
            payload.observacoes
            if "observacoes" in payload.model_fields_set
            else atual["observacoes"]
        )

        reagendado = self.repo.update_reagendamento(
            salao_id=salao_id,
            agendamento_id=agendamento_id,
            servico_id=servico_id,
            data=payload.data,
            hora_inicio=payload.hora_inicio,
            hora_fim=hora_fim,
            valor_cobrado=float(servico["preco"]),
            observacoes=novas_obs,
        )
        assert reagendado is not None
        return reagendado

    def cancelar(
        self,
        salao_id: int,
        agendamento_id: int,
        motivo: str | None = None,
    ) -> dict[str, Any]:
        atual = self.obter_agendamento(salao_id, agendamento_id)
        if atual["status"] == "CANCELADO":
            raise BusinessRuleError("Este agendamento já está cancelado.")
        if atual["status"] == "CONCLUIDO":
            raise BusinessRuleError(
                "Não é permitido cancelar um agendamento que já foi concluído."
            )

        observacoes = atual["observacoes"]
        if motivo and motivo.strip():
            prefixo = f"{observacoes} | " if observacoes else ""
            observacoes = f"{prefixo}Cancelado: {motivo.strip()}"

        cancelado = self.repo.update_status(
            salao_id=salao_id,
            agendamento_id=agendamento_id,
            status="CANCELADO",
            observacoes=observacoes,
        )
        assert cancelado is not None
        return cancelado

    def atualizar_status(
        self,
        salao_id: int,
        agendamento_id: int,
        payload: AgendamentoStatusUpdate,
    ) -> dict[str, Any]:
        if payload.status == "CANCELADO":
            return self.cancelar(
                salao_id=salao_id,
                agendamento_id=agendamento_id,
                motivo=payload.observacoes,
            )

        atual = self.obter_agendamento(salao_id, agendamento_id)
        if atual["status"] == "CANCELADO":
            raise BusinessRuleError(
                "Agendamentos cancelados não podem mudar de status. Crie um novo agendamento."
            )

        obs = (
            payload.observacoes
            if payload.observacoes is not None
            else atual["observacoes"]
        )
        atualizado = self.repo.update_status(
            salao_id=salao_id,
            agendamento_id=agendamento_id,
            status=payload.status,
            observacoes=obs,
        )
        assert atualizado is not None
        return atualizado

    def consultar_agenda_dia(self, salao_id: int, data_str: str) -> dict[str, Any]:
        try:
            data_obj = datetime.date.fromisoformat(data_str)
        except ValueError as exc:
            raise BusinessRuleError(
                "Data inválida. Utilize o formato AAAA-MM-DD."
            ) from exc

        dia_semana = data_obj.weekday()
        expediente = self.salao_repo.get_horario_por_dia_semana(salao_id, dia_semana)
        agendamentos = self.repo.list_agendamentos(salao_id=salao_id, data=data_str)

        ativos = [a for a in agendamentos if a["status"] != "CANCELADO"]
        cancelados = [a for a in agendamentos if a["status"] == "CANCELADO"]

        # Gera grade de horários de 30 em 30 minutos para visualização da agenda
        grade_horarios: list[dict[str, Any]] = []
        if expediente and expediente["aberto"]:
            h_abertura = datetime.time.fromisoformat(str(expediente["hora_abertura"]))
            h_fechamento = datetime.time.fromisoformat(str(expediente["hora_fechamento"]))
            cursor_dt = datetime.datetime.combine(data_obj, h_abertura)
            fim_dt = datetime.datetime.combine(data_obj, h_fechamento)

            while cursor_dt < fim_dt:
                slot_inicio = cursor_dt.time().strftime("%H:%M:%S")
                prox_dt = cursor_dt + datetime.timedelta(minutes=30)
                slot_fim = prox_dt.time().strftime("%H:%M:%S")

                ocupante = next(
                    (
                        a
                        for a in ativos
                        if a["hora_inicio"] < slot_fim and a["hora_fim"] > slot_inicio
                    ),
                    None,
                )
                grade_horarios.append(
                    {
                        "horario": slot_inicio[:5],
                        "disponivel": ocupante is None,
                        "agendamento_id": ocupante["id"] if ocupante else None,
                        "cliente_nome": ocupante["cliente_nome"] if ocupante else None,
                        "servico_nome": ocupante["servico_nome"] if ocupante else None,
                        "status": ocupante["status"] if ocupante else None,
                    }
                )
                cursor_dt = prox_dt

        return {
            "data": data_str,
            "dia_semana": dia_semana,
            "expediente": expediente,
            "resumo": {
                "total_dia": len(agendamentos),
                "ativos": len(ativos),
                "agendados": sum(1 for a in agendamentos if a["status"] == "AGENDADO"),
                "confirmados": sum(
                    1 for a in agendamentos if a["status"] == "CONFIRMADO"
                ),
                "concluidos": sum(
                    1 for a in agendamentos if a["status"] == "CONCLUIDO"
                ),
                "cancelados": len(cancelados),
                "faturamento_previsto_dia": round(
                    sum(float(a["valor_cobrado"]) for a in ativos), 2
                ),
            },
            "agendamentos": agendamentos,
            "grade_horarios": grade_horarios,
        }
