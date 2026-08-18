import os
from datetime import timedelta

from dotenv import load_dotenv

# Loads backend/.env into the process environment. Must run before the
# Config class below reads any os.getenv() calls.
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "hiring_agent")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@enter.in")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
