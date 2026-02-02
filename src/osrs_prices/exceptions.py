"""Custom exceptions for the OSRS Prices API client."""


class OSRSPricesError(Exception):
    """Base exception for all OSRS Prices errors."""


class APIError(OSRSPricesError):
    """Raised when the API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class ValidationError(OSRSPricesError):
    """Raised when input validation fails."""
