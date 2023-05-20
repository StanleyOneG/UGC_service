"""Module for validating configuration parameters."""

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


def to_lower(value: str) -> str:
    """Help to convert env variables to lower case.

    Args:
        value: str - string to be converted to lower case

    Returns:
        converted to lower case value
    """
    return value.lower()


class ProjectSettings(BaseSettings):
    """Configuration for the project."""

    NAME: str
    DESCRIPTION: str
    VERSION: str
    CACHE_SERVICE_NAME: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'PROJECT_'
        alias_generator = to_lower


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    HOST: str
    PORT: int

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'REDIS_'
        alias_generator = to_lower


class JwtSettings(BaseSettings):
    """Configuration for JWT."""

    PUBLIC_KEY: str

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'JWT_'
        alias_generator = to_lower


class KafkaSettings(BaseSettings):
    """Configuration for KAFKA."""

    TOPIC: str
    HOST: str
    PORT: int

    class Config:
        """Configuration class for correct env variables insertion."""

        env_prefix = 'KAFKA_'
        alias_generator = to_lower


class Settings(BaseSettings):
    """Helper class for configuration access."""

    REDIS = RedisSettings()
    PROJECT = ProjectSettings()
    JWT = JwtSettings()
    KAFKA = KafkaSettings()
