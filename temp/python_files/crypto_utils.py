"""Cryptographic utility functions."""
import hashlib
import secrets
import string

def generate_token(length: int = 32) -> str:
    """Generate a random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """Hash a string using specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode())
    return hash_obj.hexdigest()

def verify_hash(text: str, hash_value: str, algorithm: str = 'sha256') -> bool:
    """Verify if text matches hash."""
    return hash_string(text, algorithm) == hash_value
