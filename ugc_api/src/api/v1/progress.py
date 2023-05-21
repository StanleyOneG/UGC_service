"""
Progress API.

This module defines API endpoints related to progress tracking.
"""
import logging
from http import HTTPStatus
import uuid
import json

from fastapi import APIRouter, Request

from services.kafka import producer
from auth.jwt import check_auth
from db.redis import get_redis
from core.config import KAFKA_TOPIC

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/set_progress')
@check_auth(endpoint_permission='subscriber')
async def set_progress(request: Request, user_id=None):
    """
    Set the progress.

    This function sends a message to Kafka topic and Redis
    to set the progress.

    Returns:
        HTTPStatus: HTTP status code 200 (OK).
    """
    data = await request.form()
    timestamp = data.get('timestamp')
    movie_id = data.get('movie_id')
    if not timestamp:
        return HTTPStatus.BAD_REQUEST, {"msg": "timestamp not present"}
    if not user_id:
        return HTTPStatus.BAD_REQUEST, {"msg": "user_id not present"}
    if not movie_id:
        return HTTPStatus.BAD_REQUEST, {"msg": "movie_id not present"}

    topic = KAFKA_TOPIC
    value = {
        "id": str(uuid.uuid4()),
        "user_movie_id": '_'.join([str(user_id), str(movie_id)]),
        "timestamp": timestamp
    }
    encoded_value = json.dumps(value).encode()

    producer.send(
        topic=topic,
        value=encoded_value,
    )
    redis = get_redis()

    await redis.set(f'{user_id}:{movie_id}', str(timestamp))

    return HTTPStatus.OK


@router.post('/get_progress')
@check_auth(endpoint_permission='subscriber')
async def get_progress(request: Request, user_id=None):
    """
    Get the progress.

    This function gets data from Redis
    to get the progress.
    """

    # Fetch the latest records
    data = await request.json()
    movie_ids = data['movie_ids']

    redis = get_redis()

    list_of_timecodes = []
    for movie_id in movie_ids:
        timecode = await redis.get(f'{user_id}:{movie_id}')
        if timecode:
            list_of_timecodes.append({movie_id: int(timecode)})

    return list_of_timecodes
