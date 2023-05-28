"""Module for load test of MongoDB quries."""

import logging
import random
import time

import pymongo
from locust import LoadTestShape, User, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = pymongo.MongoClient(host='mongodb://mongos1,mongos2')
all_docs = client.test_database.ugc_doc.find({})
data = [data for data in all_docs]
users = [movie.get('user_id') for movie in data]
logger.info('TOTAL NUMBER OF USERS: %d', len(users))
rated_movies = [movie.get('film_id') for movie in data]
logger.info('TOTAL NUMBER OF MOVIES: %d', len(rated_movies))


class MongoLoadQueryTest(User):
    """Class for load test of MongoDB queries."""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)

        self.client = pymongo.MongoClient(
            host='mongodb://mongos1,mongos2',
        )

    @events.test_start.add_listener
    def on_test_start(environment, *args, **kwargs):
        """Event listener for test start."""
        logger.info('TEST STARTED')

    def on_start(self):
        """Set environment for user."""
        global rated_movies
        global users
        self.rated_movies = rated_movies
        self.users = users

    @task
    def get_all_docs(self):
        """Get all documents."""
        start_time = time.time()

        self.client.test_database.ugc_doc.find({})

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='get_all_docs',
            name='get_all_docs',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(2)
    def get_most_rated_films(self):
        """Get most rated films."""
        query = {'rating': {'$gte': 9}}

        start_time = time.time()

        self.client.test_database.ugc_doc.find(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='get_most_rated_films',
            name='get_most_rated_films',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(3)
    def get_most_rated_films_with_limit(self):
        """Get most rated films with limit."""
        query = {'rating': 10}

        start_time = time.time()

        self.client.test_database.ugc_doc.find(query).limit(10)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
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
        user = self.users[random.randint(0, len(self.users) - 1)]
        # query to get all bookmarks of a user
        query = [
            {'$match': {'user_id': user}},
            {'$group': {'_id': '$film_id', 'bookmarks': {'$push': '$bookmark'}}},
        ]

        start_time = time.time()

        self.client.test_database.ugc_doc.aggregate(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
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
        query = {'film_id': self.rated_movies[random.randint(0, len(self.rated_movies) - 1)]}

        start_time = time.time()

        self.client.test_database.ugc_doc.aggregate(
            [
                {'$match': query},
                {'$group': {'_id': '$film_id', 'avg_rating': {'$avg': '$rating'}}},
            ]
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='get_avg_movie_rating',
            name='get_avg_movie_rating',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    def on_stop(self):
        """Event listener for user stop event."""
        self.client.close()

    @events.test_stop.add_listener
    def on_test_stop(environment, *args, **kwargs):
        """Event listener for test stop event."""
        logger.info('TEST FINISHED')


class StagesShape(LoadTestShape):
    """Class for load test stages."""

    stages = [
        {'duration': 20, 'users': 100, 'spawn_rate': 10},
        {'duration': 40, 'users': 500, 'spawn_rate': 50},
        {'duration': 100, 'users': 1000, 'spawn_rate': 100},
        # {'duration': 200, 'users': 1500, 'spawn_rate': 100},
        # {'duration': 240, 'users': 10000, 'spawn_rate': 100},
    ]

    def tick(self):
        """Return tick data."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data

        return None
