from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.api_errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.config import settings
from app.core.openapi import configure_openapi
from app.services.intelligence_scheduler import (
    start_intelligence_scheduler,
    stop_intelligence_scheduler,
)
from app.maintenance.push_token_table import ensure_app_user_push_token_table


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        api_router,
        prefix=settings.API_V1_PREFIX,
    )

    configure_openapi(app)

    @app.get("/")
    async def root():
        return {
            "message": "PulseFi API is running",
        }

    return app


app = create_application()


@app.on_event("startup")
async def start_background_services() -> None:
    await ensure_app_user_push_token_table()
    start_intelligence_scheduler()


@app.on_event("shutdown")
async def stop_background_services() -> None:
    await stop_intelligence_scheduler()
