from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    API_V1_PREFIX: str

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BACKEND_CORS_ORIGINS: list[str]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        )
    
settings = Settings()