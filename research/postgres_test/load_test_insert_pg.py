"""Module fo load test of PostgreSQL."""


import logging
import random
import time
import uuid

from faker import Faker
from locust import HttpUser, LoadTestShape, between, events, task
from models import Movie, Review, User, UserMovie, UserMovieBookmark, UserMovieRating, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker(['en_US'])
Faker.seed(9)

random.seed(9)

movies_id = []
users_id = []
user_movie_id = []

skips = 0

create_tables()


class PostgresLoadTest(HttpUser):
    """Class for load test of PostgreSQL."""

    host = 'postgres:5432'
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Initialize testing user."""
        super().__init__(*args, **kwargs)

        self.engine = create_engine('postgresql://test:test@postgres:5432/test')

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Information about test start."""
        logger.info('TEST STARTED')

    def on_start(self):
        """Initialize testing user."""
        self.session = sessionmaker(bind=self.engine)()

    @task(10)
    def insert_movies(self):
        """Insert movie."""
        movie = uuid.uuid4()
        movies_id.append(movie)
        movie_obj = Movie(id=movie)
        start_time = time.time()
        self.session.add(movie_obj)
        self.session.commit()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='POST',
            name='insert_movie',
            response_time=processing_time,
            response_length=0,
            exception=None,
        )

    @task(10)
    def insert_users(self):
        """Insert user."""
        user = uuid.uuid4()
        users_id.append(user)
        user_obj = User(id=user)
        start_time = time.time()
        self.session.add(user_obj)
        self.session.commit()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='POST',
            name='insert_user',
            response_time=processing_time,
            response_length=0,
            exception=None,
        )

    @task(6)
    def insert_user_movie(self):
        """Insert user movie."""
        try:
            user = random.choice(users_id)
            movie = random.choice(movies_id)
            id = uuid.uuid4()
            user_movie_id.append(id)
            user_movie = UserMovie(
                id=id,
                user_id=user,
                movie_id=movie,
            )
            start_time = time.time()
            self.session.add(user_movie)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='POST',
                name='insert_user_movie',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception:
            global skips
            skips += 1

    @task(1)
    def insert_review(self):
        """Insert review."""
        try:
            user_movie = random.choice(user_movie_id)
            review = Review(
                id=uuid.uuid4(),
                user_movie_id=user_movie,
                text=fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            )
            start_time = time.time()
            self.session.add(review)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='POST',
                name='insert_review',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception as e:
            logger.error(e)
            global skips
            skips += 1

    @task(1)
    def insert_bookmark(self):
        """Insert bookmark."""
        user_movie = random.choice(user_movie_id)
        try:
            bookmark = UserMovieBookmark(
                id=uuid.uuid4(),
                user_movie_id=user_movie,
                bookmarked='True',
            )
            start_time = time.time()
            self.session.add(bookmark)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='POST',
                name='insert_bookmark',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception:
            global skips
            skips += 1

    @task(1)
    def insert_rating(self):
        """Insert rating."""
        user_movie = random.choice(user_movie_id)
        try:
            rating = UserMovieRating(
                id=uuid.uuid4(),
                user_movie_id=user_movie,
                rating=random.randint(1, 10),
            )
            start_time = time.time()
            self.session.add(rating)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='POST',
                name='insert_rating',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception:
            global skips
            skips += 1

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Information about test stop."""
        global skips
        logger.info('SKIPS %d', skips)
        logger.info('TEST FINISHED')


class StagesShape(LoadTestShape):
    """Class for load test stages."""

    stages = [
        {'duration': 20, 'users': 10, 'spawn_rate': 10},
        {'duration': 40, 'users': 100, 'spawn_rate': 10},
        {'duration': 60, 'users': 500, 'spawn_rate': 50},
        {'duration': 100, 'users': 1000, 'spawn_rate': 50},
    ]

    def tick(self):
        """Return tick data."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data

        return None
