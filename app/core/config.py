from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = Field(default="PulseFi API", validation_alias=AliasChoices("APP_NAME", "app_name"))
    APP_VERSION: str
    DEBUG: bool

    ENABLE_INTELLIGENCE_SCHEDULER: bool = False
    INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES: int = 60

    API_V1_PREFIX: str

    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    EMAIL_DELIVERY_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "PulseFi"
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    FRONTEND_ADMIN_URL: str = "http://localhost:5173"

    DATA_ENCRYPTION_KEY: str = ""
    TRUSTED_PROXY_IPS: list[str] = []

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BACKEND_CORS_ORIGINS: list[str]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.SMTP_USE_TLS and self.SMTP_USE_SSL:
            raise ValueError(
                "SMTP_USE_TLS and SMTP_USE_SSL cannot both be enabled."
            )

        if self.EMAIL_DELIVERY_ENABLED:
            missing_email_settings = [
                name
                for name, value in {
                    "SMTP_HOST": self.SMTP_HOST,
                    "SMTP_FROM_EMAIL": self.SMTP_FROM_EMAIL,
                    "FRONTEND_ADMIN_URL": self.FRONTEND_ADMIN_URL,
                }.items()
                if not value
            ]

            if missing_email_settings:
                joined = ", ".join(missing_email_settings)
                raise ValueError(
                    f"Email delivery is enabled but missing settings: {joined}."
                )

            if self.SMTP_USERNAME and not self.SMTP_PASSWORD:
                raise ValueError(
                    "Email delivery is enabled but SMTP_PASSWORD is missing for SMTP_USERNAME."
                )

        if self.DEBUG:
            return self

        if not self.EMAIL_DELIVERY_ENABLED:
            raise ValueError(
                "EMAIL_DELIVERY_ENABLED must be true when DEBUG=False."
            )

        if _is_local_frontend_url(self.FRONTEND_ADMIN_URL):
            raise ValueError(
                "FRONTEND_ADMIN_URL must not point to localhost when DEBUG=False."
            )

        if (
            len(self.SECRET_KEY) < 32
            or self.SECRET_KEY in {"your_secret_key_here", "replace_with_a_long_random_secret_key"}
        ):
            raise ValueError(
                "SECRET_KEY must be a strong non-placeholder value when DEBUG=False."
            )

        if "*" in self.BACKEND_CORS_ORIGINS:
            raise ValueError(
                "Wildcard CORS origins are not allowed when DEBUG=False."
            )

        if not self.DATA_ENCRYPTION_KEY:
            raise ValueError(
                "DATA_ENCRYPTION_KEY must be configured when DEBUG=False."
            )

        return self

    def async_database_url(self) -> str:
        database_url = self.DATABASE_URL

        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        # Neon and many Postgres providers give sslmode=require.
        # asyncpg expects ssl=require instead.
        database_url = database_url.replace("sslmode=require", "ssl=require")

        return database_url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    

def _is_local_frontend_url(value: str) -> bool:
    normalized = value.strip().lower()

    return (
        "://localhost" in normalized
        or "://127.0.0.1" in normalized
        or "://0.0.0.0" in normalized
    )

settings = Settings()
