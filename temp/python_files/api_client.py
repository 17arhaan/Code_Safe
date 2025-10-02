"""API client for external services."""
import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """Make GET request."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make POST request."""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
