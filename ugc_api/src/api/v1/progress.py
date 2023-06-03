"""
Progress API.

This module defines API endpoints related to progress tracking.
"""
import json
import logging
import uuid
from functools import lru_cache
from http import HTTPStatus

from aiokafka import AIOKafkaProducer
from auth.jwt import check_auth
from core import config
from db.redis import get_redis
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from services.kafka import get_producer


@lru_cache
def get_settings():
    """
    Get settings.

    This function returns the settings object.
    """
    return config.Settings()


settings = get_settings()
logger = logging.getLogger(__name__)
router = APIRouter()


class UserMovieProgress(BaseModel):
    """
    UserMovieProgress.

    This class defines the data model for the user movie progress.
    """

    user_id: uuid.UUID = Field(..., description='UUID of the user')
    movie_id: uuid.UUID = Field(..., description='UUID of the film')
    timestamp: int = Field(..., description='Timestamp of the progress')


class UserMovieIds(BaseModel):
    """
    UserMovieIds.

    This class defines the data model for the user movie ids.
    """

    user_id: uuid.UUID = Field(..., description='UUID of the user')
    movie_ids: list[uuid.UUID] = Field(..., description='UUID of the films')


@router.post('/set_progress')
@check_auth(endpoint_permission='subscriber')
async def set_progress(
    request: Request,
    user_movie_progress: UserMovieProgress,
    redis: Redis = Depends(get_redis),
    producer: AIOKafkaProducer = Depends(get_producer),
):
    """
    Set the progress.

    This function sends a message to Kafka topic and Redis
    to set the progress.

    Returns:
        HTTPStatus: HTTP status code 200 (OK).
    """
    # data = await request.form()
    user_id = user_movie_progress.user_id
    timestamp = user_movie_progress.timestamp
    movie_id = user_movie_progress.movie_id
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
async def get_progress(request: Request, user_movie_ids: UserMovieIds, redis: Redis = Depends(get_redis)):
    """
    Get the progress.

    This function gets data from Redis
    to get the progress.
    """
    # Fetch the latest records
    user_id = user_movie_ids.user_id
    movie_ids = user_movie_ids.movie_ids

    list_of_timecodes = []
    for movie_id in movie_ids:
        timecode = await redis.get(f'{user_id}:{movie_id}')
        if timecode:
            list_of_timecodes.append({movie_id: int(timecode)})

    return list_of_timecodes
