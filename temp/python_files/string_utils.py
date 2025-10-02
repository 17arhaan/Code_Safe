"""String manipulation utilities."""
import re

def clean_string(text: str) -> str:
    """Clean and normalize string."""
    return re.sub(r'\s+', ' ', text.strip())

def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())
