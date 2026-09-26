class InstagramError(Exception):
    """Base exception for all Instagram client related issues."""
    pass


class RateLimitException(InstagramError):
    """Raised when Instagram responds with HTTP 429 or Rate Limit error."""
    def __init__(self, message: str = "Rate limit exceeded (HTTP 429)", retry_after: int = 3600):
        super().__init__(message)
        self.retry_after = retry_after


class AuthException(InstagramError):
    """Raised when authentication or session validation fails."""
    pass


class NetworkException(InstagramError):
    """Raised when network connection or DNS resolution fails."""
    pass


class UserNotFoundException(InstagramError):
    """Raised when a requested username does not exist on Instagram."""
    pass
