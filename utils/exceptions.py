"""Custom exceptions for the Crypto Intelligence Dashboard."""


class APIError(Exception):
    """Base exception for API-related errors."""
    pass


class CoinGeckoAPIError(APIError):
    """Exception raised for CoinGecko API errors."""
    pass


class VeniceAPIError(APIError):
    """Exception raised for Venice AI API errors."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class CacheError(Exception):
    """Exception raised for cache-related errors."""
    pass


class ModelError(Exception):
    """Exception raised for ML model errors."""
    pass


class DataProcessingError(Exception):
    """Exception raised for data processing errors."""
    pass
