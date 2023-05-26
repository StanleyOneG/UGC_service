"""Module for load test of MongoDB cluster."""

import logging
import random
import time
import uuid

import pymongo
from bson import Binary
from faker import Faker
from locust import LoadTestShape, User, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker(['en_US'])
Faker.seed(9)

movies_id = [uuid.uuid4() for _ in range(1, 1_000_000)]
users_id = [uuid.uuid4() for _ in range(1, 1_000_000)]


class MongoLoadTest(User):
    """Class for load test of MongoDB cluster."""

    wait_time = between(1, 3)

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Create MongoDB client and collection."""
        logger.info('TEST STARTED.')

    def on_start(self):
        """Event listener for user start event."""
        self.client = pymongo.MongoClient(
            host='mongodb://mongors1n1:27017',
            serverSelectionTimeoutMS=5000,
        )

        self.ratings = self.client.test_database.ratings
        self.bookmarks = self.client.test_database.bookmarks
        self.reviews = self.client.test_database.reviews

    @task(7)
    def insert_rating_data(self):
        """Insert user's like in likes collection."""
        start_time = time.time()

        self.ratings.insert_one(
            {
                'film_id': Binary.from_uuid(movies_id[random.randint(0, 999_999)]),
                'user_id': Binary.from_uuid(users_id[random.randint(0, 999_999)]),
                'rating': random.randint(1, 10),
            }
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='insert_rating_data',
            name='insert_rating_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(10)
    def insert_bookmark_data(self):
        """Insert user's bookmark in likes collection."""
        start_time = time.time()

        self.bookmarks.insert_one(
            {
                'film_id': Binary.from_uuid(movies_id[random.randint(0, 999_999)]),
                'user_id': Binary.from_uuid(users_id[random.randint(0, 999_999)]),
                'bookmark': True,
            }
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='insert_bookmark_data',
            name='insert_bookmark_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(4)
    def bookmark_remove_data(self):
        """Insert user's bookmark remove in likes collection."""
        start_time = time.time()

        self.bookmarks.update_one(
            {'film_id': Binary.from_uuid(movies_id[random.randint(0, 999_999)])},
            {'$set': {'bookmark': False}},
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='bookmark_remove_data',
            name='bookmark_remove_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(2)
    def insert_review_data(self):
        """Insert user's review in likes collection."""
        start_time = time.time()

        self.reviews.insert_one(
            {
                'film_id': Binary.from_uuid(movies_id[random.randint(0, 999_999)]),
                'user_id': Binary.from_uuid(users_id[random.randint(0, 999_999)]),
                'review': fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
            }
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='insert_review_data',
            name='insert_review_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    def on_stop(self):
        """Event listener for user stop event."""
        self.client.close()

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        client = pymongo.MongoClient(
            host='mongodb://mongors1n1:27017',
            serverSelectionTimeoutMS=5000,
        )
        client.drop_database['test_database']
        client.close()
        logger.info('TEST DATABASE DROPPED')
        logger.info('TEST STOPED')


class StagesShape(LoadTestShape):
    """Class for load test stages."""

    stages = [
        {'duration': 20, 'users': 10, 'spawn_rate': 10},
        {'duration': 40, 'users': 100, 'spawn_rate': 10},
        {'duration': 60, 'users': 1000, 'spawn_rate': 50},
        {'duration': 80, 'users': 1500, 'spawn_rate': 100},
    ]

    def tick(self):
        """Return tick data."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data

        return None
