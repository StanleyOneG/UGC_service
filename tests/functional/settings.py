"""Module for tests settings."""
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()


class TestSettings(BaseSettings):

    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: str = Field(..., env='REDIS_PORT')
    redis_refresh_token_expire: int = Field(
        ...,
        env='REDIS_REFRESH_TOKEN_EXPIRE',
    )
    redis_access_token_expire: int = Field(
        ...,
        env='REDIS_ACCESS_TOKEN_EXPIRE',
    )
    service_url: str = Field(..., env='SERVICE_URL')


test_settings = TestSettings()
