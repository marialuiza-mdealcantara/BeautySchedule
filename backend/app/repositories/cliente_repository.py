"""Repositório de persistência para a entidade Clientes (isolado por salao_id)."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection


class ClienteRepository:
    """Operações de banco de dados para clientes de um salão."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    @staticmethod
    def _format(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        row["ativo"] = bool(row["ativo"])
        return row

    def list_clientes(
        self,
        salao_id: int,
        apenas_ativos: bool | None = None,
        busca: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, salao_id, nome, telefone, email, observacoes, ativo,
                   data_cadastro, data_atualizacao
            FROM clientes
            WHERE salao_id = %s
        """
        params: list[Any] = [salao_id]

        if apenas_ativos is True:
            query += " AND ativo = 1"
        elif apenas_ativos is False:
            query += " AND ativo = 0"

        if busca and busca.strip():
            termo = f"%{busca.strip()}%"
            query += " AND (nome LIKE %s OR telefone LIKE %s OR email LIKE %s)"
            params.extend([termo, termo, termo])

        query += " ORDER BY ativo DESC, nome ASC"
        rows = self.db.fetch_all(query, tuple(params))
        return [self._format(r) for r in rows if r is not None]

    def get_by_id(self, salao_id: int, cliente_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, salao_id, nome, telefone, email, observacoes, ativo,
                   data_cadastro, data_atualizacao
            FROM clientes
            WHERE id = %s AND salao_id = %s
            """,
            (cliente_id, salao_id),
        )
        return self._format(row)

    def create(
        self,
        salao_id: int,
        nome: str,
        telefone: str,
        email: str | None,
        observacoes: str | None,
    ) -> dict[str, Any]:
        new_id = self.db.execute(
            """
            INSERT INTO clientes (salao_id, nome, telefone, email, observacoes, ativo)
            VALUES (%s, %s, %s, %s, %s, 1)
            """,
            (salao_id, nome, telefone, email, observacoes),
        )
        created = self.get_by_id(salao_id, new_id)
        assert created is not None
        return created

    def update(
        self,
        salao_id: int,
        cliente_id: int,
        nome: str,
        telefone: str,
        email: str | None,
        observacoes: str | None,
        ativo: bool,
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE clientes
            SET nome = %s,
                telefone = %s,
                email = %s,
                observacoes = %s,
                ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s AND salao_id = %s
            """,
            (nome, telefone, email, observacoes, 1 if ativo else 0, cliente_id, salao_id),
        )
        return self.get_by_id(salao_id, cliente_id)

    def set_ativo(
        self, salao_id: int, cliente_id: int, ativo: bool
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE clientes
            SET ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s AND salao_id = %s
            """,
            (1 if ativo else 0, cliente_id, salao_id),
        )
        return self.get_by_id(salao_id, cliente_id)
