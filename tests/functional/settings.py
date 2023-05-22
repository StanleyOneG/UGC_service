"""Module for tests settings."""
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()


class TestSettings(BaseSettings):

    service_url: str = Field(..., env='SERVICE_URL')
    jwt_private_key: str = Field(..., env='JWT_PRIVATE_KEY')


test_settings = TestSettings()
