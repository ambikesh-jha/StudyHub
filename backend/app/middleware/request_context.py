from __future__ import annotations

import time
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import bind_request_context, clear_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or uuid4().hex
        bind_request_context(request_id=request_id)
        request.state.request_id = request_id
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            structlog.get_logger("request").error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                status_code=500,
                latency_ms=latency_ms,
                user_id=getattr(request.state, "user_id", None),
                request_id=request_id,
            )
            clear_request_context()
            raise
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        response.headers["x-request-id"] = request_id
        structlog.get_logger("request").info(
            "request_finished",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
            user_id=getattr(request.state, "user_id", None),
            request_id=request_id,
        )
        clear_request_context()
        return response
