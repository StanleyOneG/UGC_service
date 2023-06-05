"""Config."""

from pydantic import BaseSettings, Field


class ProjectSettings(BaseSettings):
    """Configuration for the project."""

    name: str = Field(..., env='PROJECT_NAME')
    description: str = Field(..., env='PROJECT_DESCRIPTION')
    version: str = Field(..., env='PROJECT_VERSION')
    cache_service_name: str = Field(..., env='PROJECT_CACHE_SERVICE_NAME')


class RedisSettings(BaseSettings):
    """Configuration for Redis."""

    host: str = Field(..., env='REDIS_HOST')
    port: int = Field(..., env='REDIS_PORT')


class JwtSettings(BaseSettings):
    """Configuration for JWT."""

    public_key: str = Field(..., env='JWT_PUBLIC_KEY')


class KafkaSettings(BaseSettings):
    """Configuration for KAFKA."""

    topic: str = Field(..., env='KAFKA_TOPIC')
    host: str = Field(..., env='KAFKA_HOST')
    port: int = Field(..., env='KAFKA_PORT')


class MongoSettings(BaseSettings):
    """Configuration for Storage."""

    database_name: str = Field(..., env='STORAGE_DATABASE_NAME')
    collection_name: str = Field(..., env='STORAGE_COLLECTION_NAME')


class AppSettings(BaseSettings):
    """Configuration for the app."""

    host: str = Field(..., env='APP_HOST')
    port: int = Field(..., env='APP_PORT')
    mongo_click_etl_frequency: int = Field(..., env='APP_MONGO_CLICK_ETL_FREQUENCY')


class Settings(BaseSettings):
    """Helper class for configuration access."""

    redis = RedisSettings()
    project = ProjectSettings()
    jwt = JwtSettings()
    kafka = KafkaSettings()
    mongodb = MongoSettings()
    app_settings = AppSettings()
