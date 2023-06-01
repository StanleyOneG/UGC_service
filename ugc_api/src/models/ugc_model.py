"""Module for ugc data models."""


import datetime
import uuid

from bson import Binary
from pydantic import BaseModel, Field


async def uuid_to_binary():
    """Convert UUID to Binary."""
    return Binary.from_uuid(uuid.uuid4())


class Review(BaseModel):
    """Class for review data model."""

    id: Binary = Field(default_factory=uuid_to_binary)
    review_body: str = Field(max_length=500)
    review_date: datetime.datetime = Field(default_factory=datetime.datetime.now)


class UGC(BaseModel):
    """Class for UGC data model."""

    film_id: Binary
    user_id: Binary
    rating: int = Field(ge=1, le=10)
    bookmark: bool = False
    review: Review = Field(default=None)
