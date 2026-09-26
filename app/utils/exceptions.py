"""
Custom exception classes for IMM.
Provides structured error handling across database, networking, rate-limiting, and configuration modules.
"""

class IMMBaseException(Exception):
    """Base exception class for all IMM specific errors."""
    def __init__(self, message: str = "An internal IMM error occurred."):
        self.message = message
        super().__init__(self.message)


class DatabaseError(IMMBaseException):
    """Raised when a SQLite database query, migration, or connection fails."""
    pass


class AuthenticationError(IMMBaseException):
    """Raised when Instagram session, cookies, or login credentials are invalid or expired."""
    pass


class RateLimitExceededError(IMMBaseException):
    """Raised when maximum hourly or daily action thresholds are hit."""
    pass


class InstagramAPIError(IMMBaseException):
    """Raised when an Instagram endpoint request fails or returns an error status."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        full_msg = f"[Status {status_code}] {message}" if status_code else message
        super().__init__(full_msg)


class ConfigurationError(IMMBaseException):
    """Raised when critical configuration settings or environment variables are invalid."""
    pass
