"""
Progress API.

This module defines API endpoints related to progress tracking.
"""
import json
import logging
import uuid
from http import HTTPStatus

from fastapi import APIRouter, Request, Depends
from auth.jwt import check_auth
from core.config import get_settings
from redis.asyncio import Redis
from db.redis import get_redis
from aiokafka import AIOKafkaProducer
from services.kafka import get_producer

settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/set_progress')
@check_auth(endpoint_permission='subscriber')
async def set_progress(request: Request,
                       user_id=None,
                       redis: Redis = Depends(get_redis),
                       producer: AIOKafkaProducer = Depends(get_producer),
                       ):
    """
    Set the progress.

    This function sends a message to Kafka topic and Redis
    to set the progress.

    Args:
        request (Request): Request instance
        user_id (str): User's id
        redis (Redis): Redis instance
        producer (AIOKafkaProducer): AIOKafkaProducer instance

    Returns:
        HTTPStatus: HTTP status code 200 (OK).
    """
    data = await request.form()
    timestamp = data.get('timestamp')
    movie_id = data.get('movie_id')
    if not timestamp:
        return HTTPStatus.BAD_REQUEST, {'msg': 'timestamp not present'}
    if not user_id:
        return HTTPStatus.BAD_REQUEST, {'msg': 'user_id not present'}
    if not movie_id:
        return HTTPStatus.BAD_REQUEST, {'msg': 'movie_id not present'}

    value = {'id': str(uuid.uuid4()), 'user_movie_id': '_'.join([str(user_id), str(movie_id)]), 'timestamp': timestamp}
    encoded_value = json.dumps(value).encode()

    await producer.send(topic=settings.kafka.topic, value=encoded_value)
    await redis.set(f'{user_id}:{movie_id}', str(timestamp))

    return HTTPStatus.OK


@router.post('/get_progress')
@check_auth(endpoint_permission='subscriber')
async def get_progress(
        request: Request,
        user_id=None, redis:
        Redis = Depends(get_redis),
):
    """
    Get the progress.

    This function gets data from Redis
    to get the progress.

    Args:
        request: (Request): Request instance
        user_id: (str): User's id
        redis (Redis): Redis instance

    Returns:
        List of timecodes for movies
    """
    # Fetch the latest records
    data = await request.json()
    movie_ids = data['movie_ids']

    list_of_timecodes = []
    for movie_id in movie_ids:
        timecode = await redis.get(f'{user_id}:{movie_id}')
        if timecode:
            list_of_timecodes.append({movie_id: int(timecode)})

    return list_of_timecodes
