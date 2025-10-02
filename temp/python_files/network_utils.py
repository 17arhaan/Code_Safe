"""Network utility functions."""
import socket
import requests
from typing import Optional

def check_port_open(host: str, port: int) -> bool:
    """Check if a port is open on a host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def get_public_ip() -> Optional[str]:
    """Get public IP address."""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return None
