import logging

from fastapi import FastAPI
from app.routers import helth_router, webhook_router

def init_app():

    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title="SimpleBot",
        description="Bot WhatsApp para atendimento de Cliente",
        version="0.0.1",
    )

    @app.on_event("startup")
    async def startup():
        app.include_router(helth_router)
        app.include_router(webhook_router)

    @app.on_event("shutdown")
    async def shutdown():
        pass

    return app


app = init_app()
