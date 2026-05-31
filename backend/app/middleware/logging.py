from app.middleware.request_context import RequestContextMiddleware


class RequestLoggingMiddleware(RequestContextMiddleware):
    """Structured request logging middleware with request IDs and latency."""
