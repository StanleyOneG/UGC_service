"""UGC API main."""
import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiokafka import AIOKafkaProducer
from api.v1 import progress, ugc_data
from core.config import get_settings
from db import redis, storage
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from logstash_async.handler import AsynchronousLogstashHandler
from redis.asyncio import Redis
from services import kafka
from services.mongodb import MongoStorage

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Execute on application startup and shutdown.

    Args:
        app: (FastApi): FastApi instance
    """
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port)
    bootstrap_server = '{host}:{port}'.format(
        host=settings.kafka.host,
        port=settings.kafka.port,
    )
    kafka.producer = AIOKafkaProducer(
        bootstrap_servers=[bootstrap_server],
        api_version='0.10.2',
    )
    storage.storage = MongoStorage(
        database_name=settings.mongodb.database_name,
        collection_name=settings.mongodb.collection_name,
    )
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
    lifespan=lifespan,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.addHandler(
    AsynchronousLogstashHandler(
        settings.logstash.host,
        settings.logstash.port,
        transport='logstash_async.transport.UdpTransport',
        database_path='logstash.db',
    )
)


@app.middleware('http')
async def log_middleware(request: Request, call_next):
    """Log request and response."""
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
app.include_router(ugc_data.router, prefix='/api/v1', tags=['UGC data'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app_settings.host,
        port=settings.app_settings.port,
    )
