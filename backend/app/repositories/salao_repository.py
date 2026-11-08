"""Repositório de dados do Salão, Usuários e Horários de Funcionamento."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection

DIAS_SEMANA_NOMES = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


class SalaoRepository:
    """Operações de persistência para informações do salão e expediente."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    def get_salao_by_id(self, salao_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, nome, cnpj, telefone, email, endereco, ativo,
                   data_cadastro, data_atualizacao
            FROM saloes
            WHERE id = %s
            """,
            (salao_id,),
        )
        if row is not None:
            row["ativo"] = bool(row["ativo"])
        return row

    def get_usuario_by_id(self, salao_id: int, usuario_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, salao_id, nome, email, cargo, ativo
            FROM usuarios
            WHERE id = %s AND salao_id = %s
            """,
            (usuario_id, salao_id),
        )
        if row is not None:
            row["ativo"] = bool(row["ativo"])
        return row

    def list_horarios_funcionamento(self, salao_id: int) -> list[dict[str, Any]]:
        rows = self.db.fetch_all(
            """
            SELECT id, salao_id, dia_semana, hora_abertura, hora_fechamento, aberto
            FROM horarios_funcionamento
            WHERE salao_id = %s
            ORDER BY dia_semana ASC
            """,
            (salao_id,),
        )
        for row in rows:
            row["aberto"] = bool(row["aberto"])
            row["dia_nome"] = DIAS_SEMANA_NOMES.get(int(row["dia_semana"]), "")
        return rows

    def get_horario_por_dia_semana(
        self, salao_id: int, dia_semana: int
    ) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, salao_id, dia_semana, hora_abertura, hora_fechamento, aberto
            FROM horarios_funcionamento
            WHERE salao_id = %s AND dia_semana = %s
            """,
            (salao_id, dia_semana),
        )
        if row is not None:
            row["aberto"] = bool(row["aberto"])
            row["dia_nome"] = DIAS_SEMANA_NOMES.get(int(row["dia_semana"]), "")
        return row
