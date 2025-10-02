"""File handling utilities."""
import os
import shutil
from pathlib import Path
from typing import List

def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

def list_files(directory: str, extension: str = None) -> List[str]:
    """List files in directory."""
    files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            if extension is None or file.endswith(extension):
                files.append(file)
    return files

def copy_file(source: str, destination: str) -> bool:
    """Copy file from source to destination."""
    try:
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False
