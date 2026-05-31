from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.auth import limiter
from app.api.v1.router import api_router
from app.core.bootstrap import seed_roles
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.cors import cors_middleware_kwargs
from app.middleware.error_handler import install_error_handlers
from app.middleware.logging import RequestLoggingMiddleware

settings = get_settings()

configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version="2.0.0")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSMiddleware, **cors_middleware_kwargs(settings.cors_origins))
install_error_handlers(app)
app.include_router(api_router)

uploads_path = Path(settings.upload_dir)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount(settings.static_url_prefix, StaticFiles(directory=uploads_path), name="uploads")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, __) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limited",
            "message": "Too many login attempts",
            "request_id": getattr(request.state, "request_id", ""),
        },
    )


@app.on_event("startup")
async def on_startup() -> None:
    await seed_roles()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
