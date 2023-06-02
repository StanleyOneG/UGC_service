"""UGC API main."""

from contextlib import asynccontextmanager
from functools import lru_cache

import uvicorn
from aiokafka import AIOKafkaProducer
from api.v1 import progress, ugc_data
from core import config
from db import redis, storage
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from services import kafka
from services.mongodb import MongoStorage


@lru_cache
def get_settings():
    """Get application settings."""
    return config.Settings()


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Execute on application startup and shutdown."""
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    kafka.producer = AIOKafkaProducer(
        bootstrap_servers=[f'{settings.kafka.host}:{settings.kafka.port}'], api_version='0.10.2'
    )
    storage.storage = MongoStorage(
        database_name=settings.mongodb.database_name, collection_name=settings.mongodb.collection_name
    )

    await kafka.producer.start()
    yield
    await redis.redis.close()
    await kafka.producer.stop()


app = FastAPI(
    title=settings.project.name,
    description=settings.project.description,
    version=settings.project.version,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(progress.router, prefix='/api/v1', tags=['progress'])
app.include_router(ugc_data.router, prefix='/api/v1', tags=['UGC data'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app_settings.host,
        port=settings.app_settings.port,
    )
