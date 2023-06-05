"""Module for ClickHouse load test - insert test."""

import logging
import random
import time
import uuid

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
        clickhouse = create_client()

        # # Create testing table
        create_query = '''
            CREATE TABLE if not exists test
            (
                movie_id String,
                progress_time Int32,
            ) ENGINE = MergeTree
            ORDER BY tuple()
        '''

        create_buffer_query = '''
            CREATE TABLE if not exists test_buffer as test
            ENGINE = Buffer(default, test, 1, 10, 100, 10000, 1000000, 10000000, 100000000)
            '''

        clickhouse.execute(create_query)
        clickhouse.execute(create_buffer_query)

        logger.info('TABLES CREATED')

        logger.info('TEST STARTED')

    def on_start(self):
        """Event listener for user start event."""
        self.clickhouse = create_client()

    @task
    def execute_insert_query_max(self):
        """Execute a sample ClickHouse query and gather statistics."""
        data = []
        for _ in range(100_000):
            movie_id = str(uuid.uuid4())
            progress_time = random.randint(1, 1_000_000)
            data.append((movie_id, progress_time))

        # # Prepare INSERT query
        query = 'INSERT INTO test (movie_id, progress_time) VALUES'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query, data)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='execute_query',
            response_time=processing_time,
            response_length=0,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        clickhouse = create_client()

        query = 'SELECT COUNT (movie_id) FROM test'

        total_rows = clickhouse.execute(query)

        logger.info('TOTAL ROWS: %s', total_rows)

        logger.info('TEST STOPPED')


class StagesShape(LoadTestShape):
    """Load test shape class."""

    stages = [
        {'duration': 100, 'users': 5, 'spawn_rate': 1},
    ]

    def tick(self):
        """Return the tick data."""
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data
        return None
