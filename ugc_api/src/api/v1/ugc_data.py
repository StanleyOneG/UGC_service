"""
UGC data API.

This module provides a Python interface to the UGC data API.
"""

import logging
import uuid

from bson import Binary
from db.storage import get_storage
from db.storage_interface import BaseStorage
from fastapi import APIRouter, Depends, HTTPException
from models.ugc_model import UGC
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class UserFilmRequest(BaseModel):
    """User film request."""

    user_id: uuid.UUID = Field(..., description='UUID of the user')
    film_id: uuid.UUID = Field(..., description='UUID of the film')


@router.post(
    '/create_user_film',
    summary='Создать пользовательскую информацию по фильму',
    description='Создать пользовательскую инофрмацию по фильму',
    tags=['UGC data'],
    response_model=UGC,
)
async def create_user_film(request: UserFilmRequest, storage: BaseStorage = Depends(get_storage)):
    """
    Create user gerenated info by film.

    Args:
        request: UserFilmRequest
        storage: BaseStorage

    Returns:
        UGC: UserFilmRequest

    Raises:
        HTTPException: 400 - if user_film already exists
    """
    requested_user_id = request.user_id
    requested_film_id = request.film_id
    user_film_doc = UGC(film_id=Binary(requested_film_id.bytes), user_id=Binary(requested_user_id.bytes))

    unique_doc = await storage.get_data({'user_id': user_film_doc.user_id, 'film_id': user_film_doc.film_id})
    logger.info(f'unique_doc: {unique_doc}')

    if unique_doc:
        raise HTTPException(status_code=400, detail='This pair of user and film already exists')

    try:
        await storage.create_data(user_film_doc.dict())

    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

    # Convert Binary fields to string representation
    user_film_doc.film_id = user_film_doc.film_id.hex()
    user_film_doc.user_id = user_film_doc.user_id.hex()

    return user_film_doc


@router.put(
    '/add_film_like',
    summary='Добавить лайк фильму по movie_id и user_id',
    description='Добавить лайк фильму',
    tags=['UGC data'],
    response_model=UGC,
)
async def add_film_like(movie_id: int, user_id: int, storage: BaseStorage = Depends(get_storage)):
    """
    Add film like.

    :param movie_id: film id
    :param user_id: user id
    :return:
    """
    pass
