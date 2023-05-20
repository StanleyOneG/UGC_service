"""
Progress API.

This module defines API endpoints related to progress tracking.
"""
import logging
from http import HTTPStatus
from typing import Annotated
import json

from fastapi import APIRouter, Request
from pydantic import BaseModel

from services.kafka import producer, consumer
from auth.jwt import check_auth
from db.redis import get_redis
from core.config import KAFKA_TOPIC

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/')
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
    timecode = data.get('timecode')
    film_id = data.get('film_id')

    if not timecode or not user_id or not film_id:
        return HTTPStatus.BAD_REQUEST

    topic = KAFKA_TOPIC
    value = str(timecode).encode()
    key = f'{user_id}:{film_id}'.encode()

    producer.send(
        topic=topic,
        value=value,
        key=key
    )
    redis = get_redis()

    await redis.set(f'{user_id}:{film_id}', str(timecode))

    return HTTPStatus.OK


@router.get('/')
@check_auth(endpoint_permission='subscriber')
async def get_progress(request: Request, user_id=None):
    """
    Get the progress.

    This function gets data from Redis
    to get the progress.
    """

    # Fetch the latest records
    data = await request.form()
    film_ids = data.get('film_ids').split(',')

    redis = get_redis()

    list_of_timecodes = []
    for film_id in film_ids:
        timecode = await redis.get(f'{user_id}:{film_id}')
        if timecode:
            list_of_timecodes.append({film_id: timecode})

    return list_of_timecodes
