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
    # reviews = relationship('Review', back_populates='user', uselist=False)
    # user_movie_rating = relationship('UserMovieRating', back_populates='user', uselist=False)
    # user_movie_bookmark = relationship('UserMovieBookmark', back_populates='user', uselist=False)
    user_movie = relationship('UserMovie', back_populates='user', uselist=False)


class Movie(Base):
    """Movie model."""

    __tablename__ = 'movie'
    id = Column(UUID(as_uuid=True), primary_key=True)
    # reviews = relationship('Review', back_populates='movie', uselist=False)
    # user_movie_rating = relationship('UserMovieRating', back_populates='movie', uselist=False)
    # user_movie_bookmark = relationship('UserMovieBookmark', back_populates='movie', uselist=False)
    user_movie = relationship('UserMovie', back_populates='movie', uselist=False)


class UserMovie(Base):
    """User's movie model."""

    __tablename__ = 'user_movie'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    movie_id = Column(UUID(as_uuid=True), ForeignKey('movie.id'))
    user = relationship('User', back_populates='user_movie', uselist=False)
    movie = relationship('Movie', back_populates='user_movie', uselist=False)
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),)


class UserMovieRating(Base):
    """User's rating of movie model."""

    __tablename__ = 'user_movie_rating'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'))
    # user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    # movie_id = Column(UUID(as_uuid=True), ForeignKey('movie.id'))
    rating = Column(Integer)
    # user = relationship('User', back_populates='user_movie_rating', uselist=False)
    # movie = relationship('Movie', back_populates='user_movie_rating', uselist=False)


class UserMovieBookmark(Base):
    """User's bookmark of movie model."""

    __tablename__ = 'user_movie_bookmark'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'))
    # user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    # movie_id = Column(UUID(as_uuid=True), ForeignKey('movie.id'))
    bookmarked = Column(String)
    # user = relationship('User', back_populates='user_movie_bookmark', uselist=False)
    # movie = relationship('Movie', back_populates='user_movie_bookmark', uselist=False)
    # __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_bookmark_uc'),)


class Review(Base):
    """Review model."""

    __tablename__ = 'review'
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_movie_id = Column(UUID(as_uuid=True), ForeignKey('user_movie.id'))
    # user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    # movie_id = Column(UUID(as_uuid=True), ForeignKey('movie.id'))
    text = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, primary_key=True)
    # user = relationship('User', back_populates='reviews', uselist=False)
    # movie = relationship('Movie', back_populates='reviews', uselist=False)


def create_tables():
    """Create tables."""
    Base.metadata.create_all(engine)
    logger.info('TABLES CREATED')


if __name__ == '__main__':
    pass
#     create_tables()
