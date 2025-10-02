"""Configuration management utilities."""
import os
from typing import Any, Dict

def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with default value."""
    return os.getenv(key, default)

def load_config_from_env(prefix: str = '') -> Dict[str, str]:
    """Load configuration from environment variables."""
    config = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config[key] = value
    return config

def set_env_var(key: str, value: str) -> None:
    """Set environment variable."""
    os.environ[key] = value
