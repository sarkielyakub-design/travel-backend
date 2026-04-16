from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 💰 PAYMENTS
    PAYSTACK_SECRET_KEY: str

    # 📧 EMAIL (MATCH fastapi-mail)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True

    # ⚙️ CONFIG
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()