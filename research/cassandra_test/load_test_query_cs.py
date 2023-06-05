"""Module for load testing Cassandra queries."""

import logging
import random
import time

from cassandra.cluster import Cluster, ConsistencyLevel
from cassandra.policies import DCAwareRoundRobinPolicy
from locust import LoadTestShape, User, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cluster = Cluster(
    contact_points=['node1', 'node2', 'node3'], load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1')
)
session = cluster.connect('test_keyspace')
session.set_keyspace('test_keyspace')
session.default_consistency_level = ConsistencyLevel.ONE
logger.info('Connected to Cassandra cluster')

movies_query = 'SELECT film_id FROM ugc_doc'
users_query = 'SELECT user_id FROM ugc_doc'
rating_movies_query = 'SELECT film_id FROM ugc_doc WHERE rating > 0 ALLOW FILTERING'
logger.info('Fetching data from Cassandra')

all_movies = session.execute(movies_query)
movies = [row.film_id for row in all_movies if row.film_id is not None]

all_users = session.execute(users_query)
users = [row.user_id for row in all_users if row.user_id is not None]
logger.info('Total number of users: %d', len(users))

all_rated_movies = session.execute(rating_movies_query)
rated_movies = [row.film_id for row in all_rated_movies if row.film_id is not None]
logger.info('Total number of movies: %d', len(rated_movies))


class CassandraLoadQueryTest(User):
    """Class for load testing Cassandra queries."""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Initialize the user class."""
        super().__init__(*args, **kwargs)

        self.cluster = Cluster(
            contact_points=['node1', 'node2', 'node3'], load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='DC1')
        )
        self.session = cluster.connect('test_keyspace')
        self.session.set_keyspace('test_keyspace')
        self.session.default_consistency_level = ConsistencyLevel.ONE

    @events.test_start.add_listener
    def on_test_start(environment, *args, **kwargs):
        """Event listener for test start."""
        logger.info('Test started')

    def on_start(self):
        """Set environment for the user."""
        global movies
        global users
        global rated_movies
        self.movies = movies
        self.users = users
        self.rated_movies = rated_movies

    @task
    def get_all_docs(self):
        """Get all documents."""
        query = 'SELECT * FROM ugc_doc'

        start_time = time.time()

        self.session.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='GET',
            name='get_all_docs',
            response_time=processing_time,
            response_length=0,
        )

    @task(2)
    def get_most_rated_films(self):
        """Get most rated films."""
        query = 'SELECT * FROM ugc_doc WHERE rating >= 9 ALLOW FILTERING'

        start_time = time.time()

        self.session.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='GET',
            name='get_most_rated_films',
            response_time=processing_time,
            response_length=0,
        )

    @task(3)
    def get_most_rated_films_with_limit(self):
        """Get most rated films with limit."""
        query = 'SELECT * FROM ugc_doc WHERE rating = 10 ALLOW FILTERING'

        start_time = time.time()

        result_set = self.session.execute(query)

        results = []
        for row in result_set:
            results.append(row)

            if len(results) >= 10:
                break

        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='GET',
            name='get_most_rated_films_with_limit',
            response_time=processing_time,
            response_length=0,
        )

    @task
    def get_bookmarks_of_user(self):
        """Get bookmarks of user."""
        user = random.choice(self.users)
        query = f'SELECT film_id, bookmark FROM ugc_doc WHERE user_id = {user} ALLOW FILTERING'

        start_time = time.time()

        self.session.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='GET',
            name='get_bookmarks_of_user',
            response_time=processing_time,
            response_length=0,
        )

    @task(4)
    def get_avg_movie_rating(self):
        """Get average movie rating."""
        movie_id = random.choice(self.rated_movies)
        query = f'SELECT AVG(rating) FROM ugc_doc WHERE film_id = {movie_id} ALLOW FILTERING'

        start_time = time.time()

        self.session.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        events.request.fire(
            request_type='GET',
            name='get_avg_movie_rating',
            response_time=processing_time,
            response_length=0,
        )

    def on_stop(self):
        """Event listener for user stop event."""
        self.session.shutdown()
        self.cluster.shutdown()

    @events.test_stop.add_listener
    def on_test_stop(environment, *args, **kwargs):
        """Event listener for test stop event."""
        logger.info('Test finished')


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
