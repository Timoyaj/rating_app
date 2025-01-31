"""
Configuration settings for the application.
"""
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
SQLITE_URL = f"sqlite:///{BASE_DIR}/content_rating.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", SQLITE_URL)

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "Content Rating API"

# Cache settings
CACHE_TTL = 3600  # 1 hour in seconds
