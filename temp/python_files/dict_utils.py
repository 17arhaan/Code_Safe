"""Dictionary manipulation utilities."""
from typing import Dict, Any

def merge_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge two dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result

def invert_dict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    """Invert dictionary keys and values."""
    return {v: k for k, v in d.items()}

def filter_dict(d: Dict[Any, Any], keys: list) -> Dict[Any, Any]:
    """Filter dictionary to only include specified keys."""
    return {k: v for k, v in d.items() if k in keys}
