"""
UGC data API.

This module provides a Python interface to the UGC data API.
"""

import logging
import uuid

from auth.jwt import check_auth
from bson import Binary
from db.storage import get_storage
from db.storage_interface import BaseStorage
from fastapi import APIRouter, Depends, HTTPException, Request
from models.ugc_model import UGC
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class UserFilmRequest(BaseModel):
    """User film request."""

    user_id: uuid.UUID = Field(..., description='UUID of the user')
    film_id: uuid.UUID = Field(..., description='UUID of the film')


class UserFilmRating(UserFilmRequest):
    """User film rating."""

    rating: int = Field(..., ge=1, le=10, description='Rating of the film')


@router.post(
    '/create_user_film',
    summary='Создать пользовательскую информацию по фильму',
    description='Создать пользовательскую инофрмацию по фильму',
    tags=['UGC data'],
    response_model=UGC,
)
@check_auth(endpoint_permission='frontend')
async def create_user_film(
    request: Request,
    user_film_request: UserFilmRequest,
    storage: BaseStorage = Depends(get_storage),
):
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
    requested_user_id = user_film_request.user_id
    requested_film_id = user_film_request.film_id
    user_film_doc = UGC(film_id=Binary(requested_film_id.bytes), user_id=Binary(requested_user_id.bytes))

    unique_doc = await storage.get_data({'user_id': user_film_doc.user_id, 'film_id': user_film_doc.film_id})

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
    '/add_user_film_rating',
    summary='Добавить рейтинг фильму по movie_id и user_id',
    description='Добавить рейтинг фильму',
    tags=['UGC data'],
    response_model=UGC,
)
@check_auth(endpoint_permission='frontend')
async def add_film_rating(
    request: Request,
    user_film_rating_request: UserFilmRating,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Add film rating.

    Args:
        request: UserFilmRating
        storage: BaseStorage

    Returns:
        UGC: UserFilmRating

    Raises:
        HTTPException: 400 - if user_film not exists
        HTTPException: 400 - if rating is not in [1, 10]
    """
    requested_user_id = user_film_rating_request.user_id
    requested_film_id = user_film_rating_request.film_id

    user_film = {'user_id': Binary(requested_user_id.bytes), 'film_id': Binary(requested_film_id.bytes)}

    try:
        await storage.update_data(user_film, {'$set': {'rating': user_film_rating_request.rating}})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

    document = await storage.get_data(user_film)
    user_film_model = UGC(**document[0])

    # Convert Binary fields to string representation
    user_film_model.film_id = user_film_model.film_id.hex()
    user_film_model.user_id = user_film_model.user_id.hex()

    return user_film_model
