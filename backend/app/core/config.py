from pydantic import model_validator
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_FOLDER_PATH = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str

    DATABASE_URL: str

    FRONTEND_URL: str

    PRODUCTION: bool

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str

    ALLOWED_HOSTS: list[str] = ["*"]

    # security
    SECRET_KEY: str

    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE: int

    REFRESH_TOKEN_EXPIRE: int

    CSRF_SECRET_KEY: str

    # allow access to self and read FRONTEND_URL

    @model_validator(mode="after")
    def set_allowed_hosts(self):
        self.ALLOWED_HOSTS.append(self.FRONTEND_URL)
        return self

    model_config = SettingsConfigDict(
        env_file=BACKEND_FOLDER_PATH / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
