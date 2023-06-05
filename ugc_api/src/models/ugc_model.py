"""Module for ugc data models."""


import datetime
import uuid

from bson import Binary
from pydantic import BaseModel, Field


class Review(BaseModel):
    """Class for review data model."""

    id: Binary = Field(default_factory=lambda: Binary.from_uuid(uuid.uuid4()))
    review_body: str = Field(max_length=500)
    review_date: datetime.datetime = Field(default_factory=datetime.datetime.now)


class UGC(BaseModel):
    """Class for UGC data model."""

    film_id: Binary = Field(default=...)
    user_id: Binary = Field(default=...)
    rating: int | None = Field(default=None, ge=1, le=10)
    bookmark: bool = Field(default=False)
    review: Review | None = Field(default=None)
    last_modified: datetime.datetime = Field(default_factory=datetime.datetime.now)
