"""Configuração de fixtures Pytest com banco de dados isolado por teste."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from backend.app.database import init_sqlite_db
from backend.app.main import app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Cria um banco SQLite temporário populado com os dados iniciais para cada teste."""
    test_db_file = tmp_path / "test_beauty_schedule.db"
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    monkeypatch.setenv("SQLITE_PATH", str(test_db_file))
    monkeypatch.setenv("DEFAULT_SALAO_ID", "1")
    monkeypatch.setenv("DEFAULT_USUARIO_ID", "1")

    init_sqlite_db(str(test_db_file), seed=True)

    with TestClient(app) as test_client:
        yield test_client

    if test_db_file.exists():
        try:
            os.remove(test_db_file)
        except OSError:
            pass
