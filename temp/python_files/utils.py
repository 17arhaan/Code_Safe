"""Utility functions for the project."""
import os
import json
from typing import Dict, List, Any

def read_config(filepath: str) -> Dict[str, Any]:
    """Read configuration from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_data(data: Any, filepath: str) -> None:
    """Save data to file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(filepath)
