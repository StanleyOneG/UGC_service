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
        logger.info('CLIENT CREATED')

        # Generate test data
        data = [(x,) for x in range(1_000_000)]  # Convert generator to a list

        # Insert testing data into staging table
        with vertica_python.connect(**connection_info) as connection:
            cursor = connection.cursor()
            cursor.execute('CREATE TABLE if not exists test (x INT);')
            cursor.executemany('INSERT INTO test (x) VALUES (%s)', data)
            logger.info('DATA INSERTED INTO TEST TABLE')
            cursor.execute(f"ALTER DATABASE {connection_info['database']} SET MaxClientSessions = 1000;")

    @task
    def execute_qery_max(self):
        """Execute a sample Vertica query and gather statistics."""
        vertica = vertica_python.connect(**connection_info)
        query = 'SELECT * FROM test LIMIT 1000;'

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            # Execute ALTER DATABASE statement to increase max_client_sessions
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='execute_qery_max',
            name='execute_qery_max',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @task(3)
    def execute_qery_min(self):
        """Execute a sample Vertica query and gather statistics."""
        vertica = vertica_python.connect(**connection_info)
        query = 'SELECT * FROM test LIMIT 100;'

        # Execute the query
        start_time = time.time()

        with vertica as connection:
            cursor = connection.cursor()
            cursor.execute(query)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='execute_qery_min',
            name='execute_qery_min',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        vertica = vertica_python.connect(**connection_info)
        with vertica as connection:
            cursor = connection.cursor()
            cursor.execute('DROP TABLE IF EXISTS test')
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
