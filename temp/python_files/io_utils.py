"""Input/Output utility functions."""
import os
from typing import List

def read_lines(filename: str) -> List[str]:
    """Read all lines from file."""
    with open(filename, 'r') as f:
        return f.readlines()

def write_lines(filename: str, lines: List[str]) -> None:
    """Write lines to file."""
    with open(filename, 'w') as f:
        f.writelines(lines)

def file_exists(filename: str) -> bool:
    """Check if file exists."""
    return os.path.isfile(filename)
