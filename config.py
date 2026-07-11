import os
from datetime import timedelta


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "ranjanpalai1976@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
