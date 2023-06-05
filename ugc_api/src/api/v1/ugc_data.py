"""
UGC data API.

This module provides a Python interface to the UGC data API.
"""

import datetime
import logging
import uuid
from http import HTTPStatus

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


class Review(BaseModel):
    """Review class."""

    id: uuid.UUID = Field(..., description='UUID of the review')
    review_body: str = Field(..., max_length=500, description='Review body')
    review_date: datetime.datetime = Field(default_factory=datetime.datetime.now, description='Review date')


class UserFilmReview(UserFilmRequest):
    """User film review."""

    review: Review = Field(..., description='Review of the film')


class UserFilmBookmark(UserFilmRequest):
    """User film bookmark."""

    bookmark: bool = Field(..., description='Bookmark of the film')


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
    if not document:
        raise HTTPException(status_code=400, detail='This pair of user and film not exists')
    user_film_model = UGC(**document[0])

    # Convert Binary fields to string representation
    user_film_model.film_id = user_film_model.film_id.hex()
    user_film_model.user_id = user_film_model.user_id.hex()
    if user_film_model.review:
        user_film_model.review.id = user_film_model.review.id.hex()
        user_film_model.review.review_date = user_film_model.review.review_date.isoformat()

    return user_film_model


@router.put(
    '/set_user_film_bookmark',
    summary='Добавить закладку фильму по movie_id и user_id',
    description='Добавить закладку фильму',
    tags=['UGC data'],
    response_model=UGC,
)
@check_auth(endpoint_permission='frontend')
async def add_film_bookmark(
    request: Request,
    user_film_bookmark_request: UserFilmBookmark,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Add film bookmark.

    Args:
        request: UserFilmBookmark
        storage: BaseStorage

    Returns:
        UGC: UserFilmBookmark

    Raises:
        HTTPException: 400 - if user_film not exists
    """
    requested_user_id = user_film_bookmark_request.user_id
    requested_film_id = user_film_bookmark_request.film_id

    user_film = {'user_id': Binary(requested_user_id.bytes), 'film_id': Binary(requested_film_id.bytes)}

    try:
        await storage.update_data(user_film, {'$set': {'bookmark': user_film_bookmark_request.bookmark}})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

    document = await storage.get_data(user_film)
    if not document:
        raise HTTPException(status_code=400, detail='This pair of user and film not exists')
    user_film_model = UGC(**document[0])

    # Convert Binary fields to string representation
    user_film_model.film_id = user_film_model.film_id.hex()
    user_film_model.user_id = user_film_model.user_id.hex()
    if user_film_model.review:
        user_film_model.review.id = user_film_model.review.id.hex()
        user_film_model.review.review_date = user_film_model.review.review_date.isoformat()

    return user_film_model


@router.put(
    '/add_user_film_review',
    summary='Добавить отзыв фильму по movie_id и user_id',
    description='Добавить отзыв фильму',
    tags=['UGC data'],
    response_model=UGC,
)
@check_auth(endpoint_permission='frontend')
async def add_film_review(
    request: Request,
    user_film_review_request: UserFilmReview,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Add film review.

    Args:
        request: UserFilmReview
        storage: BaseStorage

    Returns:
        UGC: UserFilmReview

    Raises:
        HTTPException: 400 - if user_film not exists
    """
    requested_user_id = user_film_review_request.user_id
    requested_film_id = user_film_review_request.film_id

    user_film = {'user_id': Binary(requested_user_id.bytes), 'film_id': Binary(requested_film_id.bytes)}
    user_film_review = {
        'id': Binary(user_film_review_request.review.id.bytes),
        'review_body': user_film_review_request.review.review_body,
        'review_date': user_film_review_request.review.review_date,
    }

    try:
        await storage.update_data(user_film, {'$set': {'review': user_film_review}})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

    document = await storage.get_data(user_film)
    if not document:
        raise HTTPException(status_code=400, detail='This pair of user and film not exists')
    user_film_model = UGC(**document[0])

    # Convert Binary fields to string representation
    user_film_model.film_id = user_film_model.film_id.hex()
    user_film_model.user_id = user_film_model.user_id.hex()
    user_film_model.review.id = user_film_model.review.id.hex()
    user_film_model.review.review_date = user_film_model.review.review_date.isoformat()

    return user_film_model


@router.get(
    '/get_user_film_info',
    summary='Получить пользовательскую информацию по фильму по movie_id и user_id',
    description='Получить пользовательскую инофрмацию по фильму',
    tags=['UGC data'],
    response_model=UGC,
)
@check_auth(endpoint_permission='frontend')
async def get_user_film_info(
    request: Request,
    user_id: uuid.UUID,
    film_id: uuid.UUID,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Get user film info.

    Args:
        request: UserFilmRequest
        storage: BaseStorage

    Returns:
        UGC: UserFilmRequest

    Raises:
        HTTPException: 400 - if user_film not exists
    """
    requested_user_id = user_id
    requested_film_id = film_id

    user_film = {'user_id': Binary(requested_user_id.bytes), 'film_id': Binary(requested_film_id.bytes)}

    document = await storage.get_data(user_film)
    if not document:
        raise HTTPException(status_code=400, detail='This pair of user and film not exists')
    user_film_model = UGC(**document[0])

    # Convert Binary fields to string representation
    user_film_model.film_id = user_film_model.film_id.hex()
    user_film_model.user_id = user_film_model.user_id.hex()
    if user_film_model.review:
        user_film_model.review.id = user_film_model.review.id.hex()
        user_film_model.review.review_date = user_film_model.review.review_date.isoformat()

    return user_film_model


@router.delete(
    '/delete_user_film_info',
    summary='Удалить пользовательскую инофрмацию по фильму по movie_id и user_id',
    description='Удалить пользовательскую инофрмацию по фильму',
    tags=['UGC data'],
)
@check_auth(endpoint_permission='frontend')
async def delete_user_film_info(
    request: Request,
    user_film_info_request: UserFilmRequest,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Delete user film info.

    Args:
        request: UserFilmRequest
        storage: BaseStorage

    Returns:
        UGC: UserFilmRequest

    Raises:
        HTTPException: 400 - if user_film not exists
    """
    requested_user_id = user_film_info_request.user_id
    requested_film_id = user_film_info_request.film_id

    user_film = {'user_id': Binary(requested_user_id.bytes), 'film_id': Binary(requested_film_id.bytes)}

    document = await storage.get_data(user_film)
    if not document:
        raise HTTPException(status_code=400, detail='This pair of user and film not exists')

    try:
        await storage.delete_data(user_film)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

    return HTTPStatus.OK


@router.get(
    '/get_movie_avg_rating',
    summary='Получить среднюю оценку фильма по movie_id',
    description='Получить среднее значение оценки фильма',
    tags=['UGC data'],
)
@check_auth(endpoint_permission='frontend')
async def get_movie_avg_rating(
    request: Request,
    movie_id: uuid.UUID,
    storage: BaseStorage = Depends(get_storage),
):
    """
    Get movie avg rating.

    Args:
        request: uuid.UUID
        storage: BaseStorage

    Returns:
        float: movie avg rating

    Raises:
        HTTPException: 400 - if movie not exists
    """
    movie = {'film_id': Binary(movie_id.bytes)}
    document = await storage.get_data(movie)
    found_movie_models = [UGC(**movie) for movie in document]

    if not found_movie_models:
        raise HTTPException(status_code=400, detail='Error: movie not found')

    movie_avg_rating = sum([movie.rating for movie in found_movie_models]) / len(found_movie_models)
    return movie_avg_rating
