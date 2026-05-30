from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

class Settings(BaseSettings):
    APP_NAME: str = Field(default="PulseFi API", validation_alias=AliasChoices("APP_NAME", "app_name"))
    APP_VERSION: str
    DEBUG: bool

    ENABLE_INTELLIGENCE_SCHEDULER: bool = False
    INTELLIGENCE_SCHEDULER_INTERVAL_MINUTES: int = Field(default=60, ge=1)

    API_V1_PREFIX: str

    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    EMAIL_DELIVERY_ENABLED: bool = False
    EMAIL_DELIVERY_PROVIDER: str = "brevo"
    BREVO_API_KEY: str = ""
    BREVO_API_URL: str = "https://api.brevo.com/v3/smtp/email"
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "PulseFi"
    FRONTEND_ADMIN_URL: str = "http://localhost:5173"

    DATA_ENCRYPTION_KEY: str = ""
    TRUSTED_PROXY_IPS: list[str] = []

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_USER_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 30, ge=1)

    BACKEND_CORS_ORIGINS: list[str]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.EMAIL_DELIVERY_ENABLED:
            email_provider = self.EMAIL_DELIVERY_PROVIDER.strip().lower()

            if email_provider != "brevo":
                raise ValueError("EMAIL_DELIVERY_PROVIDER must be 'brevo'.")

            required_email_settings = {
                "BREVO_API_KEY": self.BREVO_API_KEY,
                "SMTP_FROM_EMAIL": self.SMTP_FROM_EMAIL,
                "FRONTEND_ADMIN_URL": self.FRONTEND_ADMIN_URL,
            }

            missing_email_settings = [
                name
                for name, value in required_email_settings.items()
                if not value
            ]

            if missing_email_settings:
                joined = ", ".join(missing_email_settings)
                raise ValueError(
                    f"Email delivery is enabled but missing settings: {joined}."
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
        return _sanitize_asyncpg_database_url(self.DATABASE_URL)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    

def _sanitize_asyncpg_database_url(database_url: str) -> str:
    """Return a SQLAlchemy asyncpg URL that accepts Neon-style params."""
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )

    parsed = urlsplit(database_url)
    if not parsed.query:
        return database_url

    sanitized_params: list[tuple[str, str]] = []
    has_ssl_param = False

    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = key.lower()

        if normalized_key == "channel_binding":
            continue

        if normalized_key == "ssl":
            has_ssl_param = True
            sanitized_params.append((key, value))
            continue

        if normalized_key == "sslmode":
            if value.lower() == "require" and not has_ssl_param:
                sanitized_params.append(("ssl", "require"))
                has_ssl_param = True
            continue

        sanitized_params.append((key, value))

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(sanitized_params, doseq=True),
            parsed.fragment,
        )
    )

def _is_local_frontend_url(value: str) -> bool:
    normalized = value.strip().lower()

    return (
        "://localhost" in normalized
        or "://127.0.0.1" in normalized
        or "://0.0.0.0" in normalized
    )

settings = Settings()
