from __future__ import annotations

import traceback
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import StudyHubError


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StudyHubError)
    async def handle_studyhub_error(request: Request, exc: StudyHubError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", ""),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "request_id": getattr(request.state, "request_id", ""),
                "details": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": str(exc.detail),
                "request_id": getattr(request.state, "request_id", ""),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger = structlog.get_logger("error")
        logger.error(
            "unhandled_exception",
            request_id=getattr(request.state, "request_id", ""),
            traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", ""),
            },
        )

