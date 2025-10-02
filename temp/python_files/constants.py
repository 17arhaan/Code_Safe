"""Application constants."""
import os

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# Database Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME', 'app_db')

# File Paths
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')
LOG_DIR = os.getenv('LOG_DIR', './logs')

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
VERSION = '1.0.0'
