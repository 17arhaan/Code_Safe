"""Error handling utilities."""
import logging
from typing import Callable, Any

def retry_on_failure(max_retries: int = 3):
    """Decorator to retry function on failure."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logging.warning(f"Attempt {attempt + 1} failed: {e}")
            return None
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> tuple:
    """Safely execute function and return result and error."""
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        return None, e
