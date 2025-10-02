"""Random utility functions."""
import random
import string
from typing import List, Any

def random_string(length: int = 10) -> str:
    """Generate random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_choice(items: List[Any]) -> Any:
    """Choose random item from list."""
    return random.choice(items)

def shuffle_list(items: List[Any]) -> List[Any]:
    """Shuffle a list in place."""
    random.shuffle(items)
    return items
