"""Repositório de persistência para a entidade Serviços (isolado por salao_id)."""

from __future__ import annotations

from typing import Any
from backend.app.database import DatabaseConnection


class ServicoRepository:
    """Operações de banco de dados para o catálogo de serviços do salão."""

    def __init__(self, db: DatabaseConnection) -> None:
        self.db = db

    @staticmethod
    def _format(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        row["ativo"] = bool(row["ativo"])
        row["duracao_minutos"] = int(row["duracao_minutos"])
        row["preco"] = float(row["preco"])
        return row

    def list_servicos(
        self,
        salao_id: int,
        apenas_ativos: bool | None = None,
        busca: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, salao_id, nome, descricao, duracao_minutos, preco, ativo,
                   data_cadastro, data_atualizacao
            FROM servicos
            WHERE salao_id = %s
        """
        params: list[Any] = [salao_id]

        if apenas_ativos is True:
            query += " AND ativo = 1"
        elif apenas_ativos is False:
            query += " AND ativo = 0"

        if busca and busca.strip():
            termo = f"%{busca.strip()}%"
            query += " AND (nome LIKE %s OR descricao LIKE %s)"
            params.extend([termo, termo])

        query += " ORDER BY ativo DESC, nome ASC"
        rows = self.db.fetch_all(query, tuple(params))
        return [self._format(r) for r in rows if r is not None]

    def get_by_id(self, salao_id: int, servico_id: int) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, salao_id, nome, descricao, duracao_minutos, preco, ativo,
                   data_cadastro, data_atualizacao
            FROM servicos
            WHERE id = %s AND salao_id = %s
            """,
            (servico_id, salao_id),
        )
        return self._format(row)

    def get_by_nome(self, salao_id: int, nome: str) -> dict[str, Any] | None:
        row = self.db.fetch_one(
            """
            SELECT id, salao_id, nome, descricao, duracao_minutos, preco, ativo,
                   data_cadastro, data_atualizacao
            FROM servicos
            WHERE salao_id = %s AND LOWER(nome) = LOWER(%s)
            """,
            (salao_id, nome.strip()),
        )
        return self._format(row)

    def create(
        self,
        salao_id: int,
        nome: str,
        descricao: str | None,
        duracao_minutos: int,
        preco: float,
    ) -> dict[str, Any]:
        new_id = self.db.execute(
            """
            INSERT INTO servicos (salao_id, nome, descricao, duracao_minutos, preco, ativo)
            VALUES (%s, %s, %s, %s, %s, 1)
            """,
            (salao_id, nome, descricao, duracao_minutos, preco),
        )
        created = self.get_by_id(salao_id, new_id)
        assert created is not None
        return created

    def update(
        self,
        salao_id: int,
        servico_id: int,
        nome: str,
        descricao: str | None,
        duracao_minutos: int,
        preco: float,
        ativo: bool,
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE servicos
            SET nome = %s,
                descricao = %s,
                duracao_minutos = %s,
                preco = %s,
                ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s AND salao_id = %s
            """,
            (
                nome,
                descricao,
                duracao_minutos,
                preco,
                1 if ativo else 0,
                servico_id,
                salao_id,
            ),
        )
        return self.get_by_id(salao_id, servico_id)

    def set_ativo(
        self, salao_id: int, servico_id: int, ativo: bool
    ) -> dict[str, Any] | None:
        self.db.execute(
            """
            UPDATE servicos
            SET ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s AND salao_id = %s
            """,
            (1 if ativo else 0, servico_id, salao_id),
        )
        return self.get_by_id(salao_id, servico_id)
