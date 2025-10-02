"""Useful decorators."""
import time
import functools
from typing import Callable, Any

def timing(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def memoize(func: Callable) -> Callable:
    """Decorator to cache function results."""
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper
