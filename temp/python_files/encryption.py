"""Encryption utilities."""
import hashlib
import base64
from cryptography.fernet import Fernet

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_key() -> bytes:
    """Generate encryption key."""
    return Fernet.generate_key()

def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using Fernet."""
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using Fernet."""
    f = Fernet(key)
    decoded = base64.b64decode(encrypted_data.encode())
    decrypted = f.decrypt(decoded)
    return decrypted.decode()
