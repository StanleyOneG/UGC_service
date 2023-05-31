import logging
import random
import time
import uuid

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
        with vertica_python.connect(**connection_info) as connection:
            cursor = connection.cursor()
            cursor.execute('CREATE TABLE if not exists test (movie_id VARCHAR(36) PRIMARY KEY, progress_time INT);')
            cursor.execute(f"ALTER DATABASE {connection_info['database']} SET MaxClientSessions = 1000;")
        logger.info('TABLE CREATED')
        logger.info('TEST STARTED')

    @task
    def execute_insert_query_max(self):
        """Execute a sample Vertica query and gather statistics."""
        # Generate test data
        data = []
        for _ in range(100_000):
            movie_id = str(uuid.uuid4())
            progress_time = random.randint(1, 1_000_000)
            data.append((movie_id, progress_time))

        start_time = time.time()
        # Insert testing data into staging table
        with vertica_python.connect(**connection_info) as connection:
            cursor = connection.cursor()
            cursor.executemany('INSERT INTO test (movie_id, progress_time) VALUES (%s, %s)', data)

        processing_time = int((time.time() - start_time) * 1000)

        # Gather statistics
        events.request.fire(
            request_type='POST',
            name='Insert data',
            response_time=processing_time,
            response_length=0,
            context=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for test stop event."""
        with vertica_python.connect(**connection_info) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT COUNT (movie_id) FROM test;')
            total_rows = cursor.fetchone()[0]

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
