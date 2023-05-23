"""Module for tests settings."""
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    """Class for tests settings."""

    service_url: str = Field(..., env='SERVICE_URL')
    jwt_private_key: str = Field(..., env='JWT_PRIVATE_KEY')
