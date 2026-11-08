"""Ponto de entrada principal da API FastAPI — BeautySchedule."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import get_settings
from backend.app.exceptions import DomainError
from backend.app.routers import agenda, agendamentos, clientes, relatorios, salao, servicos

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(
    title="BeautySchedule API",
    description=(
        "SaaS de gerenciamento de agendamentos, clientes e serviços para salões de beleza "
        "em arquitetura de 3 camadas."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    """Converte exceções de domínio em respostas JSON padronizadas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": True,
            "mensagem": exc.message,
            "detail": exc.message,
        },
    )


@app.get("/api/health", tags=["Infraestrutura"])
def health_check() -> dict[str, Any]:
    """Verifica a disponibilidade da API e informa o motor de banco configurado."""
    settings = get_settings()
    return {
        "status": "ok",
        "aplicacao": "BeautySchedule",
        "versao": "1.0.0",
        "ambiente": settings.app_env,
        "db_engine": settings.db_engine,
    }


# Registro dos roteadores da camada de aplicação
app.include_router(salao.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(agendamentos.router)
app.include_router(agenda.router)
app.include_router(relatorios.router)

# Servir arquivos estáticos do Frontend (Camada de Apresentação)
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/", include_in_schema=False)
    def serve_frontend() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))
