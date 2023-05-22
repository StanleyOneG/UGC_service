"""Module for ClickHouse load test."""

import logging
import time

from config.conf import create_client
from locust import LoadTestShape, User, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClickHouseLoadTest(User):
    """Test class for load testing ClickHouse."""

    wait_time = between(1, 3)  # Wait time between consecutive tasks

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Event listener for test start event. Perform any setup operations on test start."""
        logger.info('TEST STARTED')

    def on_start(self):
        """Event listener for user start event."""
        self.clickhouse = create_client()

    @task(1)
    def average_progress_time(self):
        """Execute a sample ClickHouse query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT AVG(progress_time) FROM test'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='average_progress_time',
            name='average_progress_time',
            response_time=processing_time,
            response_length=0,
        )

    @task(2)
    def find_movie_with_longest_progress_time(self):
        """Execute a sample ClickHouse query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT movie_id, progress_time FROM test WHERE progress_time = (SELECT MAX(progress_time) FROM test)'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='movie_with_longest_progress_time',
            name='movie_with_longest_progress_time',
            response_time=processing_time,
            response_length=0,
        )

    @task(1)
    def find_progress_by_range(self):
        """Execute a sample ClickHouse query and gather statistics."""
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
            GROUP BY duration_range
        '''

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='progress_by_range',
            name='progress_by_range',
            response_time=processing_time,
            response_length=0,
        )

    @task(3)
    def calculate_total_progress(self):
        """Execute a sample ClickHouse query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT SUM(progress_time) FROM test'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='total_progress',
            name='total_progress',
            response_time=processing_time,
            response_length=0,
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
