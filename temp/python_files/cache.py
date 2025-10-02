"""Simple caching mechanism."""
import time
from typing import Any, Optional

class Cache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
