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
        clickhouse = create_client()

        data = ((x,) for x in range(10_000_000))

        # Create testing table
        create_query = 'CREATE TABLE if not exists test (x Int32) ENGINE = Memory'
        clickhouse.execute(create_query)

        logger.info('TABLE CREATED')

        # Prepare INSERT query
        query = 'INSERT INTO test (x) VALUES'

        # Batch insert the data
        clickhouse.execute(query, data)
        logger.info('DATA INSERTED')

        logger.info('TEST STARTED')

    def on_start(self):
        """Event listener for user start event."""
        self.clickhouse = create_client()

    @task(1)
    def execute_query_max(self):
        """Execute a sample ClickHouse query and gather statistics."""
        # Prepare SELECT query
        query = 'SELECT * FROM test LIMIT 1000'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='execute_query',
            name='execute_query',
            response_time=processing_time,
            response_length=0,
        )

    @task(3)
    def execute_query_min(self):
        """Execute a sample ClickHouse query and gather statistics."""
        global clickhouse
        # Prepare SELECT query
        query = 'SELECT * FROM test LIMIT 100'

        # Execute the query
        start_time = time.time()
        self.clickhouse.execute(query)
        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='execute_query',
            name='execute_query',
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
        {'duration': 40, 'users': 100, 'spawn_rate': 10},
        {'duration': 60, 'users': 1000, 'spawn_rate': 100},
        {'duration': 100, 'users': 1500, 'spawn_rate': 100},
    ]

    def tick(self):
        """Return the tick data."""
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data
        return None
