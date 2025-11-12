"""
Custom error classes for consistent API error handling.
"""


class AppError(Exception):
    """Base application error with status code."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppError):
    """Resource not found (404)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ValidationError(AppError):
    """Invalid input (400)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ServiceUnavailableError(AppError):
    """External service unavailable (503)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=503)
