"""Module fo load test of PostgreSQL."""


import logging
import random
import time
import uuid

from faker import Faker
from locust import HttpUser, LoadTestShape, between, events, task
from models import Movie, Review, User, UserMovieBookmark, UserMovieRating, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker(['en_US'])
Faker.seed(9)

random.seed(9)

movies_id = []
users_id = []

skips = 0

create_tables()


class PostgresLoadTest(HttpUser):
    """Class for load test of PostgreSQL."""

    host = 'postgres:5432'
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Initialize testing user."""
        super().__init__(*args, **kwargs)

        engine = create_engine('postgresql://test:test@postgres:5432/test')
        Session = sessionmaker(bind=engine)
        self.session = Session()

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Information about test start."""
        logger.info('TEST STARTED')

    @task(4)
    def insert_movies(self):
        """Insert movie."""
        movie_id = uuid.uuid4()
        movies_id.append(movie_id)
        movie = Movie(id=movie_id)
        start_time = time.time()
        self.session.add(movie)
        self.session.commit()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='insert_movie',
            name='insert_movie',
            response_time=processing_time,
            response_length=0,
            exception=None,
        )

    @task(4)
    def insert_users(self):
        """Insert user."""
        user_id = uuid.uuid4()
        users_id.append(user_id)
        user = User(id=user_id)
        start_time = time.time()
        self.session.add(user)
        self.session.commit()
        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='insert_user',
            name='insert_user',
            response_time=processing_time,
            response_length=0,
            exception=None,
        )

    @task(1)
    def insert_review(self):
        """Insert review."""
        try:
            movie_id = random.choice(movies_id)
            user_id = random.choice(users_id)
            review = Review(
                id=uuid.uuid4(),
                movie_id=movie_id,
                user_id=user_id,
                text=fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            )
            start_time = time.time()
            self.session.add(review)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='insert_review',
                name='insert_review',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception as e:
            logger.error(e)
            global skips
            skips += 1

    @task(2)
    def insert_bookmark(self):
        """Insert bookmark."""
        try:
            bookmark = UserMovieBookmark(
                id=uuid.uuid4(),
                user_id=random.choice(users_id),
                movie_id=random.choice(movies_id),
                bookmarked='True',
            )
            start_time = time.time()
            self.session.add(bookmark)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='insert_bookmark',
                name='insert_bookmark',
                response_time=processing_time,
                response_length=0,
                exception=None,
            )

        except Exception:
            global skips
            skips += 1

    @task
    def insert_rating(self):
        """Insert rating."""
        try:
            rating = UserMovieRating(
                id=uuid.uuid4(),
                user_id=random.choice(users_id),
                movie_id=random.choice(movies_id),
                rating=random.randint(1, 10),
            )
            start_time = time.time()
            self.session.add(rating)
            self.session.commit()
            processing_time = int((time.time() - start_time) * 1000)

            events.request.fire(
                request_type='insert_rating',
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
        logger.info('TEST FINISHED')

        # engine = create_engine('postgresql://test:test@postgres:5432/test')
        # Session = sessionmaker(bind=engine)
        # session = Session()

        # metadata_obj.drop_all(engine)
        # logger.info('SCHEMA DROPED')


class StagesShape(LoadTestShape):
    """Class for load test stages."""

    stages = [
        {'duration': 20, 'users': 10, 'spawn_rate': 10},
        # {'duration': 40, 'users': 100, 'spawn_rate': 10},
        # {'duration': 60, 'users': 500, 'spawn_rate': 50},
        # {'duration': 100, 'users': 1000, 'spawn_rate': 50},
    ]

    def tick(self):
        """Return tick data."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data

        return None
