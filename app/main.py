import logging

from fastapi import FastAPI
from app.routers import helth_router, webhook_router
from contextlib import asynccontextmanager

logger = None  # Declaração no nível do módulo

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação FastAPI, incluindo as rotas durante a inicialização."""
    # Código de inicialização
    app.include_router(helth_router)
    app.include_router(webhook_router)
    yield
    # Código de finalização
    pass

def init_app():
    """Inicializa a aplicação FastAPI com as configurações básicas e rotas."""

    logging.basicConfig(level=logging.ERROR)
    global logger
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title="SimpleBot",
        description="Bot WhatsApp para atendimento de Cliente",
        version="0.0.1",
        lifespan=lifespan
    )

    return app


app = init_app()
