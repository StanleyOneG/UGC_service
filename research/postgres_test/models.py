"""Module for postgreSQL models."""

import logging

from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, String, UniqueConstraint, create_engine, schema
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine('postgresql://test:test@postgres:5432/test')

with engine.connect() as conn:
    if not conn.dialect.has_schema(conn, 'test'):
        conn.execute(schema.CreateSchema('test', True))
        conn.commit()

metadata_obj = MetaData(schema='test')
Base = declarative_base(metadata=metadata_obj)


class User(Base):
    """User model."""

    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key=True)


class Movie(Base):
    """Movie model."""

    __tablename__ = 'movie'
    id = Column(UUID(as_uuid=True), primary_key=True)


class UserMovie(Base):
    """UserMovie model."""

    __tablename__ = 'user_movie'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), index=True)
    movie_id = Column(UUID(as_uuid=True), ForeignKey('movie.id'), index=True)
    movie = relationship('Movie')
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie'),)


class UserMovieRating(Base):
    """User's rating of movie model."""

    __tablename__ = 'user_movie_rating'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'))
    rating = Column(Integer)
    user_movie = relationship(UserMovie)


class UserMovieBookmark(Base):
    """User's bookmark of movie model."""

    __tablename__ = 'user_movie_bookmark'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'))
    bookmarked = Column(String)
    user_movie = relationship(UserMovie)


class Review(Base):
    """Review model."""

    __tablename__ = 'review'
    id = Column(UUID(as_uuid=True), primary_key=True)
    text = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, primary_key=True)
    # likes = relationship('UserReviewLike', back_populates='user')
    __table_args__ = (UniqueConstraint('id', name='_review_id_uc'),)


class UserMovieReview(Base):
    """User's review of movie model."""

    __tablename__ = 'user_movie_review'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'), index=True)
    review_id = Column(UUID(as_uuid=True), ForeignKey('review.id'), index=True)
    user_movie = relationship(UserMovie)
    review = relationship(Review)
    __table_args__ = (UniqueConstraint('user_movie_id', 'review_id', name='_user_movie_review_uc'),)


# class UserReviewLike(Base):
#     """User's like of review model."""

#     __tablename__ = 'user_review_like'
#     id = Column(UUID(as_uuid=True), primary_key=True)
#     user_review_id = Column(UUID(as_uuid=True), ForeignKey('user_movie_review.id'))
#     user_review = relationship(UserMovieReview)


def create_tables():
    """Create tables."""
    Base.metadata.create_all(engine)
    logger.info('TABLES CREATED')


# if __name__ == "__main__":
#     create_tables()
