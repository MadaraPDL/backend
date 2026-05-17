from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    API_V1_PREFIX: str

    DATABASE_URL: str
    TEST_DATABASE_URL: str | None = None

    EMAIL_DELIVERY_ENABLED: bool = False
    DATA_ENCRYPTION_KEY: str = ""
    TRUSTED_PROXY_IPS: list[str] = []

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BACKEND_CORS_ORIGINS: list[str]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.DEBUG:
            return self

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
settings = Settings()
