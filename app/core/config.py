from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, SecretStr


class Settings(BaseSettings):
    # ==========================
    # DATABASE
    # ==========================
    DATABASE_URL: str

    # ==========================
    # FRONTEND
    # ==========================
    FRONTEND_URL: str

    # ==========================
    # PAYSTACK
    # ==========================
    PAYSTACK_SECRET_KEY: SecretStr

    # ==========================
    # EMAIL
    # ==========================
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: EmailStr
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True

    # Optional
    MAIL_FROM_NAME: str = "M.Y Hamdala Travel & Tours"

    # ==========================
    # PYDANTIC CONFIG
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()