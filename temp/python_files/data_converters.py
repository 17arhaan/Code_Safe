"""Data conversion utilities."""
import json
import csv
from typing import List, Dict, Any

def dict_to_json(data: Dict[Any, Any], indent: int = 2) -> str:
    """Convert dictionary to JSON string."""
    return json.dumps(data, indent=indent)

def json_to_dict(json_str: str) -> Dict[Any, Any]:
    """Convert JSON string to dictionary."""
    return json.loads(json_str)

def list_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """Convert list of dictionaries to CSV file."""
    if not data:
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
