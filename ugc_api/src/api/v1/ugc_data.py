"""
UGC data API.

This module provides a Python interface to the UGC data API.
"""

import logging

from fastapi import APIRouter
from models.ugc_model import UGC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    '/add_film_like',
    summary='Добавить лайк фильму по movie_id и user_id',
    description='Добавить лайк фильму',
    tags=['UGC data'],
    response_model=UGC,
)
async def add_film_like(movie_id: int, user_id: int):
    """
    Add film like.

    :param movie_id: film id
    :param user_id: user id
    :return:
    """
    pass
