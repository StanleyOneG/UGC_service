"""Module for Vertica load test."""

import logging
import time

import vertica_python
from locust import LoadTestShape, User, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


connection_info = {
    'host': 'vertica',
    'port': 5433,
    'user': 'dbadmin',
    'password': '',
    'database': 'docker',
    'autocommit': True,
}


class VerticaLoadTest(User):
    """Vertica load test class."""

    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        """Initialize the load test."""
        super().__init__(*args, **kwargs)
        self.vertica = None

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Event listener for test start event."""
        logger.info('TEST STARTED')

    @task(2)
    def find_movie_with_longest_progress_time(self):
        """Execute a sample Vertica query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT movie_id, progress_time FROM test WHERE progress_time = (SELECT MAX(progress_time) FROM test);'
        vertica = vertica_python.connect(**connection_info)

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            # Execute ALTER DATABASE statement to increase max_client_sessions
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='GET',
            name='movie_with_longest_progress_time',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(1)
    def average_progress_time(self):
        """Execute a sample Vertica query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT AVG(progress_time) FROM test;'
        vertica = vertica_python.connect(**connection_info)

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='GET',
            name='average_progress_time',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(1)
    def find_progress_by_range(self):
        """Execute a sample Vertica query and gather statistics."""
        # Prepare SELECT query
        query = '''
            SELECT
                CASE
                    WHEN progress_time <= 60000 THEN '0-60 seconds'
                    WHEN progress_time <= 300000 THEN '1-5 minutes'
                    WHEN progress_time <= 1800000 THEN '5-30 minutes'
                    ELSE 'More than 30 minutes'
                END AS duration_range,
                COUNT(*) AS count
            FROM test
            GROUP BY duration_range;
        '''

        vertica = vertica_python.connect(**connection_info)

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='GET',
            name='progress_by_range',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(3)
    def calculate_total_progress(self):
        """Execute a sample Vertica query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT SUM(progress_time) FROM test'
        vertica = vertica_python.connect(**connection_info)

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='GET',
            name='total_progress',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        logger.info('TEST STOPPED')


class StagesShape(LoadTestShape):
    """Load test shape class."""

    stages = [
        {'duration': 20, 'users': 10, 'spawn_rate': 1},
        {'duration': 40, 'users': 100, 'spawn_rate': 5},
        {'duration': 120, 'users': 500, 'spawn_rate': 10},
    ]

    def tick(self):
        """Return the tick data."""
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data
        return None
