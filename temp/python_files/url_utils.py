"""URL manipulation utilities."""
from urllib.parse import urlparse, urljoin
from typing import Optional

def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc
    except:
        return None

def join_urls(base: str, path: str) -> str:
    """Join base URL with path."""
    return urljoin(base, path)
