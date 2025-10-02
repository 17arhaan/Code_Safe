"""List manipulation utilities."""
from typing import List, Any

def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicates from list."""
    return list(set(items))

def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a nested list."""
    return [item for sublist in nested_list for item in sublist]

def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [items[i:i + size] for i in range(0, len(items), size)]
