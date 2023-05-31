"""Module for load test of Cassandra cluster."""

import logging
import random
import time
import uuid

from cassandra.cluster import Cluster, ConsistencyLevel
from cassandra.policies import DCAwareRoundRobinPolicy
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


class CassandraLoadTest(User):
    """Class for load test of Cassandra cluster."""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)

        self.cluster = Cluster(
            contact_points=['node1', 'node2', 'node3'], load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1')
        )
        self.session = self.cluster.connect()

        self.session.execute(
            """
            CREATE KEYSPACE IF NOT EXISTS test_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3}
            """
        )
        self.session.set_keyspace('test_keyspace')
        self.session.default_consistency_level = ConsistencyLevel.ONE

        self.session.execute(
            """
            CREATE TABLE IF NOT EXISTS ugc_doc (
                film_id UUID PRIMARY KEY,
                user_id UUID,
                rating INT,
                bookmark BOOLEAN,
                review MAP<UUID, TEXT>
            )
            """
        )

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Information about test start."""
        logger.info('TEST STARTED.')

    @task(3)
    def insert_user_data(self):
        """Insert user's like in ugc_doc table."""
        start_time = time.time()

        film_id = random.choice(movies_id)
        user_id = random.choice(users_id)
        review_id = uuid.uuid4()

        query = """
            INSERT INTO ugc_doc (film_id, user_id, rating, bookmark, review)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            film_id,
            user_id,
            random.randint(1, 10),
            False,
            {review_id: fake.paragraph(nb_sentences=5, variable_nb_sentences=True)},
        )

        try:
            self.session.execute(query, params)

        except Exception:
            pass
            global skips
            skips += 1

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='insert_user_data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_rating(self):
        """Update movie rating."""
        film_id = random.choice(movies_id)

        query = """
            UPDATE ugc_doc SET rating = %s
            WHERE film_id = %s
        """
        params = (random.randint(1, 10), film_id)

        start_time = time.time()

        self.session.execute(query, params)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='update_movie_rating',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_bookmark(self):
        """Update movie bookmark."""
        film_id = random.choice(movies_id)

        query = """
            UPDATE ugc_doc SET bookmark = %s
            WHERE film_id = %s
        """
        params = (True, film_id)

        start_time = time.time()

        self.session.execute(query, params)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='update_movie_bookmark',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task
    def update_movie_review_likes(self):
        """Update movie review likes."""
        film_id = random.choice(movies_id)
        review_id = uuid.uuid4()

        query = """
            UPDATE ugc_doc SET review[%s] = %s
            WHERE film_id = %s
        """
        params = (review_id, fake.paragraph(nb_sentences=5, variable_nb_sentences=True), film_id)

        start_time = time.time()

        self.session.execute(query, params)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='update_movie_review_likes',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    def on_stop(self):
        """Event listener for user stop event."""
        self.cluster.shutdown()

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        cluster = Cluster(
            contact_points=['node1', 'node2', 'node3'], load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1')
        )
        session = cluster.connect('test_keyspace')

        row = session.execute('SELECT COUNT(*) FROM ugc_doc')[0]
        documents_count = row[0]
        logger.info('TOTAL NUMBER OF DOCUMENTS %d', documents_count)
        global skips
        logger.info('TOTAL SKIPS %d', skips)
        logger.info('TEST STOPPED')


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
