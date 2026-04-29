import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # --------------------------
    # Core settings
    # --------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # --------------------------
    # Database settings
    # --------------------------
    # Use PostgreSQL by default; fallback to SQLite if DATABASE_URL not set
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://scanner_user:Yitayh2334@localhost:5432/ai_scanner"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------------
    # JWT settings
    # --------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-super-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # --------------------------
    # CORS settings
    # --------------------------
    CORS_HEADERS = "Content-Type"

    # --------------------------
    # Uploads / Reports
    # --------------------------
    REPORT_FOLDER = os.getenv("REPORT_FOLDER", "reports")