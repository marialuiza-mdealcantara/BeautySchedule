"""Exceções de domínio para a camada de regras de negócio do BeautySchedule."""

from __future__ import annotations


class DomainError(Exception):
    """Erro base de regra de negócio."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(DomainError):
    """Recurso não encontrado no salão atual."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=404)


class ConflictError(DomainError):
    """Conflito de horário na agenda ou duplicidade de registro."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=409)


class BusinessRuleError(DomainError):
    """Violação de regra de negócio (ex: fora do expediente, cliente inativo)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=422)
