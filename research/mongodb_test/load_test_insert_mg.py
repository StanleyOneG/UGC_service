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

random.seed(9)

movies_id = [uuid.uuid4() for _ in range(1, 500_000)]
users_id = [uuid.uuid4() for _ in range(1, 1_000_000)]

skips = 0


class MongoLoadTest(User):
    """Class for load test of MongoDB cluster."""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)

        self.client = pymongo.MongoClient(
            host='mongodb://mongos1,mongos2',
        )

        self.db = self.client.test_database
        self.ugc_doc = self.db.ugc_doc

        self.ugc_doc.create_index([('film_id', pymongo.ASCENDING)], unique=True)
        self.ugc_doc.create_index([('user_id', pymongo.ASCENDING)], unique=True)

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Inforation about test start."""
        logger.info('TEST STARTED.')

    @task(3)
    def insert_user_data(self):
        """Insert user's like in likes collection."""
        start_time = time.time()

        try:
            self.ugc_doc.insert_one(
                {
                    'film_id': Binary.from_uuid(movies_id[random.randint(0, 499_999)]),
                    'user_id': Binary.from_uuid(users_id[random.randint(0, 999_999)]),
                    'rating': random.randint(1, 10),
                    'bookmark': False,
                    'review': {
                        'id': Binary.from_uuid(uuid.uuid4()),
                        'review_body': fake.paragraph(nb_sentences=5, variable_nb_sentences=True),
                        'review_date': int(time.time()),
                        'likes': [Binary.from_uuid(users_id[random.randint(0, 999_999)])],
                        'dislikes': [Binary.from_uuid(users_id[random.randint(0, 999_999)])],
                    },
                }
            )

        except pymongo.errors.DuplicateKeyError:
            pass
            global skips
            skips += 1

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='insert_user_data',
            name='insert_user_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_rating(self):
        """Update movie data."""
        filter_query = {'film_id': Binary.from_uuid(movies_id[random.randint(0, 499_999)])}

        update_query = {'$set': {'rating': random.randint(1, 10)}}

        start_time = time.time()

        self.ugc_doc.update_one(filter_query, update_query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='update_movie_rating',
            name='update_movie_rating',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_bookmark(self):
        """Update movie data."""
        filter_query = {'film_id': Binary.from_uuid(movies_id[random.randint(0, 499_999)])}

        update_query = {'$set': {'bookmark': True}}

        start_time = time.time()

        self.ugc_doc.update_one(filter_query, update_query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='update_movie_bookmark',
            name='insert_rating_bookmark',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_review_likes(self):
        """Update movie data."""
        filter_query = {'film_id': Binary.from_uuid(movies_id[random.randint(0, 499_999)])}

        update_query = {'$push': {'review.likes': Binary.from_uuid(users_id[random.randint(0, 999_999)])}}

        start_time = time.time()

        self.ugc_doc.update_one(filter_query, update_query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='update_movie_review_likes',
            name='update_movie_review_likes',
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
            host='mongodb://mongos1,mongos2',
            serverSelectionTimeoutMS=5000,
        )
        # client.drop_database('test_database')
        # client.close()
        # logger.info('TEST DATABASE DROPPED')

        documents_count = client.test_database.ugc_doc.count_documents({})
        logger.info('TOTAL NUMBER OF DOCUMENTS %d', documents_count)
        global skips
        logger.info('TOTAL SKIPS %d', skips)
        logger.info('TEST STOPED')


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
