from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Options Intelligence"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str

    LOG_LEVEL: str = "INFO"
    GROWW_API_KEY: str
    GROWW_API_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
