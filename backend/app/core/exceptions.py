from __future__ import annotations


class StudyHubError(Exception):
    def __init__(self, message: str, error: str | None = None, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.error = error or self.__class__.__name__
        self.status_code = status_code


class NotFoundError(StudyHubError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, error="not_found", status_code=404)


class UnauthorizedError(StudyHubError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, error="unauthorized", status_code=401)


class ForbiddenError(StudyHubError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, error="forbidden", status_code=403)


class ConflictError(StudyHubError):
    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(message, error="conflict", status_code=409)


class GoneError(StudyHubError):
    def __init__(self, message: str = "Resource expired") -> None:
        super().__init__(message, error="gone", status_code=410)

