"""UGC API main."""
import logging
from functools import lru_cache
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from aiokafka import AIOKafkaProducer
import sentry_sdk
from logstash_async.handler import AsynchronousLogstashHandler

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


sentry_sdk.init(
    dsn=settings.sentry.dns,
    traces_sample_rate=1.0,
)

app = FastAPI(
    title=settings.project.name,
    description=settings.project.description,
    version=settings.project.version,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.addHandler(AsynchronousLogstashHandler(
    settings.logstash.host,
    settings.logstash.port,
    transport='logstash_async.transport.UdpTransport',
    database_path='logstash.db',
))


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    response = await call_next(request)
    client_host = request.client.host
    method = request.method
    url = request.url

    if 'X-Request-ID' in request.headers:
        request_id = request.headers['X-Request-ID']
        response.headers['X-Request-ID'] = request_id

    logger.info(f"{client_host} - \"{method} {url}\" {response.status_code}", extra=response.headers)
    return response


app.include_router(progress.router, prefix='/api/v1', tags=['progress'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
