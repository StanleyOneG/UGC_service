"""UGC API main."""

import uvicorn
from api.v1 import progress
from core import config
from db import redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from aiokafka import AIOKafkaProducer
from services import kafka
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Execute on application startup and shutdown"""
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    kafka.producer = AIOKafkaProducer(
        bootstrap_servers=[f'{config.KAFKA_HOST}:{config.KAFKA_PORT}'])
    await kafka.producer.start()
    yield
    await redis.redis.close()
    await kafka.producer.close()

app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.PROJECT_VERSION,
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
