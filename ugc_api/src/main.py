"""UGC API main."""

from functools import lru_cache
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from aiokafka import AIOKafkaProducer
from api.v1 import progress
from db import redis
from services import kafka
from core import config


@lru_cache
def get_settings():
    return config.Settings()


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Execute on application startup and shutdown"""
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    kafka.producer = AIOKafkaProducer(
        bootstrap_servers=[f'{settings.kafka.host}:{settings.kafka.port}'],
        api_version='0.10.2')
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
    lifespan=lifespan
)


app.include_router(progress.router, prefix='/api/v1', tags=['progress'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
