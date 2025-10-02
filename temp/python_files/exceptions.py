"""Custom exception classes."""

class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class NetworkError(Exception):
    """Raised when network operation fails."""
    pass

class DatabaseError(Exception):
    """Raised when database operation fails."""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class AuthorizationError(Exception):
    """Raised when authorization fails."""
    pass
