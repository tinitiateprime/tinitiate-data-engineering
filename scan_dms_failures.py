# main-function\mt-dm-lambda-src\core\config.py
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App Metadata ---
    APP_NAME: str = "mt-dm-lambda-main-function"
    ENV: str = "dev"
    LOG_LEVEL: str = "DEBUG"

    # --- Database Configuration ---
    DB_NAME: str = "default-db"
    DB_USER: str = "default-user"
    DB_PASSWORD: str = "default-password"
    DB_HOST: str = "host-fake"
    DB_PORT: int = 5432
    # Connection Pool Settings
    DB_POOL_MAXCONN: int = 10
    DB_CONNECT_TIMEOUT_SECONDS: int = 30
    DB_STATEMENT_TIMEOUT_MS: int = 29000

    # --- Synth Database Configuration ---
    SYNTH_DB_NAME: str = "synth-db"
    SYNTH_DB_USER: str = "synth-user"
    SYNTH_DB_PASSWORD: str = "synth-password"
    SYNTH_DB_HOST: str = "synth-host-fake"
    SYNTH_DB_PORT: int = 5432

    # AWS Logging Related
    AWS_LAMBDA_LOG_GROUP_NAME: Optional[str] = None
    AWS_LAMBDA_LOG_STREAM_NAME: Optional[str] = None

    # --- Shared Business Logic Constants ---
    MAX_PAGE_SIZE: int = 10000
    DEFAULT_PAGE_SIZE: int = 100  # Field(default=20, gt=0, lt=MAX_PAGE_SIZE + 1)

    # --- Session Storage Related
    SESSION_TABLE_NAME: str = (
        "mt-dm-sessions"  # Suffix is added -dev for example in service
    )
    SESSION_EXPIRES_TTL_SECONDS: int = 3600

    # --- Okta Related
    OKTA_ISSUER_URL: str = "https://hii-test.oktapreview.com/oauth2/default"
    OKTA_CLIENT_ID: str = "0oax97u2rcNm3z44N1d7"
    OKTA_CLIENT_SECRET: str = "Y0DARRk1jQO86ncqQbYSzbeWpMVbLGtmpGKblrowxJL_UBIUrpNGiuWUh_j5-VbI"  # TODO: Move to TF Vault
    OKTA_REDIRECT_URI: str = (
        "https://mt-dm-data.hii-next-dev.com/dev/v1/auth/okta/callback"
    )
    OKTA_SCOPES: str = "openid profile email"

    @property
    def DATABASES(self) -> dict:
        return {
            "default": {
                "dbname": self.DB_NAME,
                "user": self.DB_USER,
                "password": self.DB_PASSWORD,
                "host": self.DB_HOST,
                "port": self.DB_PORT,
            },
            "synth": {
                "dbname": self.SYNTH_DB_NAME,
                "user": self.SYNTH_DB_USER,
                "password": self.SYNTH_DB_PASSWORD,
                "host": self.SYNTH_DB_HOST,
                "port": self.SYNTH_DB_PORT,
            },
        }

    # Configuration to read from .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Prevents crashing if extra env vars are present
    )


# Create a singleton instance to be imported by other layers
settings = Settings()



++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
connection.py
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


