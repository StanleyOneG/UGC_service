"""
Progress API.

This module defines API endpoints related to progress tracking.
"""
import logging
from http import HTTPStatus

from fastapi import APIRouter
from services.kafka import producer

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/set_progress')
def set_progress():
    """
    Set the progress.

    This function sends a message to the 'topic_ugc' Kafka topic
    to set the progress.

    Returns:
        HTTPStatus: HTTP status code 200 (OK).
    """
    producer.send(
        topic='topic_ugc',
        value=b'1611039931',
        key=b'500271+tt0120338',
    )
    return HTTPStatus.OK
