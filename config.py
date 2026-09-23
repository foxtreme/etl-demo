from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str
    database_url: str
    github_org: str = "microsoft"
    request_timeout: int = Field(default=10, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=1, ge=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
