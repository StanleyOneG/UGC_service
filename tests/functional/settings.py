"""Module for tests settings."""
from pydantic import BaseSettings, Field
# from psycopg2 import connect
from dotenv import load_dotenv

load_dotenv()


class TestSettings(BaseSettings):
    # db_engine: str = Field(..., env='DB_ENGINE')
    # pg_host: str = Field(..., env='POSTGRES_HOST')
    # pg_port: str = Field(..., env='POSTGRES_PORT')
    # pg_user: str = Field(..., env='POSTGRES_USER')
    # pg_password: str = Field(..., env='POSTGRES_PASSWORD')
    # pg_db: str = Field(..., env='POSTGRES_DB')
    # db_uri = (
    #     f"{db_engine}://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    # )
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
    auth_service_url: str = Field(..., env='AUTH_SERVICE_URL')


test_settings = TestSettings()

# psycopg2 connection to postgres database
# conn = connect(
#     host=test_settings.pg_host,
#     port=test_settings.pg_port,
#     user=test_settings.pg_user,
#     password=test_settings.pg_password,
#     database=test_settings.pg_db,
#     options="-c search_path=auth",
# )
# conn.autocommit = True
