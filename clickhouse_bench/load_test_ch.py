"""Module for ClickHouse load test."""

import random
import string

from clickhouse_driver import Client
from locust import HttpUser, between, events, task


class ClickHouseLoadTest(HttpUser):
    """Test class for load testing ClickHouse."""

    wait_time = between(1, 3)  # Wait time between consecutive tasks
    client = None

    @events.test_start.add_listener
    def on_test_start(self, **kwargs):
        """Event listener for test start event. Perform any setup operations on test start."""
        # ClickHouse connection configuration
        connection_settings = {
            'host': 'localhost',
            'port': 8123,
            'user': 'default',
            'password': '',
            'database': 'default',
        }

        # Create a ClickHouse client
        self.client = Client(**connection_settings)

        # Generate and insert random data
        data = []
        for _ in range(10000000):
            random_string = ''.join(random.choices(string.ascii_lowercase, k=10))
            random_number = random.randint(1, 100)
            data.append((random_string, random_number))

        # Prepare INSERT query
        query = 'INSERT INTO my_table (string_column, int_column) VALUES'

        # Batch insert the data
        self.client.execute(query, data)

        # Other setup operations you may want to perform on test start

    @task
    def execute_query(self):
        """Execute a sample ClickHouse query and gather statistics."""
        # Generate random data
        random_string = ''.join(random.choices(string.ascii_lowercase, k=10))
        random_number = random.randint(1, 100)

        # Prepare SELECT query
        query = f"SELECT * FROM my_table WHERE string_column = '{random_string}' AND int_column = {random_number}"

        # Execute the query
        response_time_start = self.client.get_current_time_in_millis()
        self.client.execute(query)
        response_time = self.client.get_current_time_in_millis() - response_time_start

        # Gather statistics
        self.environment.events.request_success.fire(
            request_type='execute_query',
            name='execute_query',
            response_time=response_time,
            response_length=0,
        )
