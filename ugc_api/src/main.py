"""UGC API main."""

import uvicorn
from api.v1 import progress
from core import config
from db import redis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.PROJECT_VERSION,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """Execute on application startup."""
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


@app.on_event('shutdown')
async def shutdown():
    """Execute on application shutdown."""
    await redis.redis.close()


app.include_router(progress.router, prefix='/api/v1', tags=['progress'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
