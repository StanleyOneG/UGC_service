"""Module fo load test of PostgreSQL."""


import logging
import random
import time
import uuid

from faker import Faker
from locust import HttpUser, LoadTestShape, between, events, task
from models import Movie, create_tables
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker(['en_US'])
Faker.seed(9)

random.seed(9)

movies_id = [uuid.uuid4() for _ in range(1, 500_000)]
users_id = [uuid.uuid4() for _ in range(1, 1_000_000)]

skips = 0

create_tables()
logger.info('Tables created')


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

    @task
    def insert_movies(self):
        """Insert movie."""
        movie_id = random.choice(movies_id)
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

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Information about test stop."""
        logger.info('TEST FINISHED')


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
