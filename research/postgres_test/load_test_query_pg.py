"""Module for load test of PostgreSQL queries."""


import logging
import random
import time

from locust import HttpUser, LoadTestShape, between, events, task
from models import Movie, User, UserMovie, UserMovieBookmark, UserMovieRating
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

random.seed(9)

engige = create_engine('postgresql://test:test@postgres:5432/test')

Session = sessionmaker(bind=engige)
session = Session()

all_users = [str(user._asdict().get('id')) for user in session.query(User.id).all()]
all_movies = [str(movie._asdict().get('id')) for movie in session.query(Movie.id).all()]

logger.info(f'Loaded {len(all_users)} users and {len(all_movies)} movies.')


class PostgresLoadQueryTest(HttpUser):
    """Class for load test of PostgreSQL queries."""

    host = 'postgres:5432'
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        super().__init__(*args, **kwargs)

        global session
        self.session = session
        self.users = all_users
        self.movies = all_movies

    @events.test_start.add_listener
    def on_test_start(environment, *args, **kwargs):
        """Event listener for test start."""
        logger.info('TEST STARTED')

    @task
    def get_all_users(self):
        """Get all users."""
        start_time = time.time()
        self.session.query(User).all()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_all_users',
            name='get_all_users',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def get_all_movies(self):
        """Get all movies."""
        start_time = time.time()
        self.session.query(Movie).all()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_all_movies',
            name='get_all_movies',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def get_most_rated_films(self):
        """Get most rated films."""
        start_time = time.time()
        self.session.query(Movie).join(UserMovie, UserMovie.movie_id == Movie.id).join(
            UserMovieRating, UserMovieRating.user_movie_id == UserMovie.id
        ).filter(UserMovieRating.rating == 10).all()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_most_rated_films',
            name='get_most_rated_films',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def get_most_rated_films_with_limit(self):
        """Get most rated films with limit."""
        start_time = time.time()
        self.session.query(Movie).join(UserMovie, UserMovie.movie_id == Movie.id).join(
            UserMovieRating, UserMovieRating.user_movie_id == UserMovie.id
        ).filter(UserMovieRating.rating == 10).limit(10).all()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_most_rated_films_with_limit',
            name='get_most_rated_films_with_limit',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def get_bookmarks_of_user(self):
        """Get bookmarks of user."""
        start_time = time.time()
        user = random.choice(self.users)
        self.session.query(UserMovieBookmark).join(UserMovie, UserMovieBookmark.user_movie_id == UserMovie.id).filter(
            UserMovie.user_id == user
        ).all()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_bookmarks_of_user',
            name='get_bookmarks_of_user',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def get_avg_movie_rating(self):
        """Get avg movie rating."""
        start_time = time.time()
        movie = random.choice(self.movies)
        self.session.query(func.avg(UserMovieRating.rating)).join(
            UserMovie, UserMovieRating.user_movie_id == UserMovie.id
        ).filter(UserMovie.movie_id == movie).scalar()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='get_avg_movie_rating',
            name='get_avg_movie_rating',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, *args, **kwargs):
        """Event listener for test stop."""
        logger.info('TEST STOPPED')


class StagesShape(LoadTestShape):
    """Class for load test stages."""

    stages = [
        {'duration': 20, 'users': 100, 'spawn_rate': 10},
        {'duration': 40, 'users': 500, 'spawn_rate': 50},
        {'duration': 100, 'users': 1000, 'spawn_rate': 100},
    ]

    def tick(self):
        """Return tick data."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data

        return None
