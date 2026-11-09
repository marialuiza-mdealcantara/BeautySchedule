"""Repositório de persistência para Agendamentos e Consultas de Agenda/Relatórios."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection


class AgendamentoRepository:
    """Operações de banco de dados para agendamentos de um salão."""

    BASE_SELECT = """
        SELECT
            a.id,
            a.salao_id,
            a.cliente_id,
            c.nome AS cliente_nome,
            c.telefone AS cliente_telefone,
            a.servico_id,
            s.nome AS servico_nome,
            s.duracao_minutos AS servico_duracao_minutos,
            a.usuario_id,
            u.nome AS usuario_nome,
            a.data,
            a.hora_inicio,
            a.hora_fim,
            a.status,
            a.canal_origem,
            a.observacoes,
            a.valor_cobrado,
            a.data_cadastro,
            a.data_atualizacao
        FROM agendamentos a
        INNER JOIN clientes c
            ON c.id = a.cliente_id AND c.salao_id = a.salao_id
        INNER JOIN servicos s
            ON s.id = a.servico_id AND s.salao_id = a.salao_id
        LEFT JOIN usuarios u
            ON u.id = a.usuario_id AND u.salao_id = a.salao_id
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    @staticmethod
    def _format(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        row["valor_cobrado"] = float(row["valor_cobrado"])
        row["servico_duracao_minutos"] = int(row["servico_duracao_minutos"])
        return row

    def get_by_id(self, salao_id: int, agendamento_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            f"{self.BASE_SELECT} WHERE a.id = %s AND a.salao_id = %s",
            (agendamento_id, salao_id),
        )
        return self._format(row)

    def list_agendamentos(
        self,
        salao_id: int,
        data: str | None = None,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        cliente_id: int | None = None,
        servico_id: int | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        query = f"{self.BASE_SELECT} WHERE a.salao_id = %s"
        params: list[Any] = [salao_id]

        if data:
            query += " AND a.data = %s"
            params.append(data)
        if data_inicio:
            query += " AND a.data >= %s"
            params.append(data_inicio)
        if data_fim:
            query += " AND a.data <= %s"
            params.append(data_fim)
        if cliente_id is not None:
            query += " AND a.cliente_id = %s"
            params.append(cliente_id)
        if servico_id is not None:
            query += " AND a.servico_id = %s"
            params.append(servico_id)
        if status:
            query += " AND a.status = %s"
            params.append(status.upper())

        query += " ORDER BY a.data ASC, a.hora_inicio ASC"
        rows = self.db.fetch_all(query, tuple(params))
        return [self._format(r) for r in rows if r is not None]

    def find_conflicting_agendamentos(
        self,
        salao_id: int,
        data: str,
        hora_inicio: str,
        hora_fim: str,
        exclude_agendamento_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Busca agendamentos ativos (não cancelados) que tenham interseção de horário."""
        query = f"""
            {self.BASE_SELECT}
            WHERE a.salao_id = %s
              AND a.data = %s
              AND a.status != 'CANCELADO'
              AND a.hora_inicio < %s
              AND a.hora_fim > %s
        """
        params: list[Any] = [salao_id, data, hora_fim, hora_inicio]
        if exclude_agendamento_id is not None:
            query += " AND a.id != %s"
            params.append(exclude_agendamento_id)

        rows = self.db.fetch_all(query, tuple(params))
        return [self._format(r) for r in rows if r is not None]

    def create(
        self,
        salao_id: int,
        cliente_id: int,
        servico_id: int,
        usuario_id: int | None,
        data: str,
        hora_inicio: str,
        hora_fim: str,
        canal_origem: str,
        observacoes: str | None,
        valor_cobrado: float,
    ) -> dict[str, Any]:
        new_id = self.db.execute(
            """
            INSERT INTO agendamentos (
                salao_id, cliente_id, servico_id, usuario_id,
                data, hora_inicio, hora_fim, status,
                canal_origem, observacoes, valor_cobrado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'AGENDADO', %s, %s, %s)
            """,
            (
                salao_id,
                cliente_id,
                servico_id,
                usuario_id,
                data,
                hora_inicio,
                hora_fim,
                canal_origem,
                observacoes,
                valor_cobrado,
            ),
        )
        created = self.get_by_id(salao_id, new_id)
        assert created is not None
        return created

    def update_reagendamento(
        self,
        salao_id: int,
        agendamento_id: int,
        servico_id: int,
        data: str,
        hora_inicio: str,
        hora_fim: str,
        valor_cobrado: float,
        observacoes: str | None,
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE agendamentos
            SET servico_id = %s,
                data = %s,
                hora_inicio = %s,
                hora_fim = %s,
                valor_cobrado = %s,
                observacoes = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s AND salao_id = %s
            """,
            (
                servico_id,
                data,
                hora_inicio,
                hora_fim,
                valor_cobrado,
                observacoes,
                agendamento_id,
                salao_id,
            ),
        )
        return self.get_by_id(salao_id, agendamento_id)

    def update_status(
        self,
        salao_id: int,
        agendamento_id: int,
        status: str,
        observacoes: str | None = None,
    ) -> dict[str, Any] | None:
        if observacoes is not None:
            self.db.execute(
                """
                UPDATE agendamentos
                SET status = %s,
                    observacoes = %s,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = %s AND salao_id = %s
                """,
                (status, observacoes, agendamento_id, salao_id),
            )
        else:
            self.db.execute(
                """
                UPDATE agendamentos
                SET status = %s,
                    data_atualizacao = CURRENT_TIMESTAMP
                WHERE id = %s AND salao_id = %s
                """,
                (status, agendamento_id, salao_id),
            )
        return self.get_by_id(salao_id, agendamento_id)
