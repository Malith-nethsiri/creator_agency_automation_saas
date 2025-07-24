from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Creator Agency Automation SaaS"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]

    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""  # From email address
    EMAIL_FROM_NAME: str = "Creator Agency Automation"

    # Stripe Configuration
    STRIPE_SECRET_KEY: str = "sk_test_..."
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_..."
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_SUCCESS_URL: str = "http://localhost:3000/success"
    STRIPE_CANCEL_URL: str = "http://localhost:3000/cancel"

    # Docker & Production
    ENVIRONMENT: str = "development"  # development, staging, production
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    LOG_LEVEL: str = "info"

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # ✅ Prevents errors from extra env keys


settings = Settings()
