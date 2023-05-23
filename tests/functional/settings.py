"""Module for tests settings."""
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()


class TestSettings(BaseSettings):
    """Class for tests settings."""

    service_url: str = Field(..., env='SERVICE_URL')
    jwt_private_key: str = Field(..., env='JWT_PRIVATE_KEY')


test_settings = TestSettings()
