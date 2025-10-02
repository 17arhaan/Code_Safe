"""Performance monitoring utilities."""
import time
import psutil
from typing import Callable, Any

def measure_memory(func: Callable) -> Callable:
    """Decorator to measure memory usage of function."""
    def wrapper(*args, **kwargs) -> Any:
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        result = func(*args, **kwargs)
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory used: {memory_after - memory_before:.2f} MB")
        return result
    return wrapper

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
        'memory_available': psutil.virtual_memory().available / 1024 / 1024 / 1024,  # GB
    }
