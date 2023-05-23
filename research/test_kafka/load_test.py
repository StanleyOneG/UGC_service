"""Module for load testing of Kafka."""

import logging
import random
import time
import uuid

from config import get_kafka_producer
from locust import HttpUser, LoadTestShape, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

topic = 'test'

producer = get_kafka_producer()


class KafkaLoadTest(HttpUser):
    """Test class for load testing of Kafka."""

    wait_time = between(1, 3)

    host = 'kafka-1:29092'

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Event listener for user start event."""
        logger.info('TEST STARTED')

    @task
    def produce_messages(self):
        """Produce messages to Kafka and gather statistics."""
        global producer
        # Produce messages to Kafka
        message = '-'.join([str(uuid.uuid4()), str(random.randint(1, 10000))])
        request_time_start = time.time()
        producer.produce(topic, value=message.encode('utf-8'))

        # Flush the producer to ensure the message is sent immediately
        producer.flush()

        processing_time = int((time.time() - request_time_start) * 1000)

        events.request.fire(
            request_type='produce_messages',
            name='produce_messages',
            response_time=processing_time,
            response_length=0,
            context=None,
            exception=None,
        )

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Event listener for user stop event."""
        logger.info('TEST STOPPED')


class StagesShape(LoadTestShape):
    """Load test shape class."""

    stages = [
        {'duration': 20, 'users': 10, 'spawn_rate': 1},
        {'duration': 40, 'users': 100, 'spawn_rate': 10},
        {'duration': 60, 'users': 1000, 'spawn_rate': 50},
        {'duration': 160, 'users': 1500, 'spawn_rate': 50},
        {'duration': 180, 'users': 5000, 'spawn_rate': 100},
        {'duration': 240, 'users': 10000, 'spawn_rate': 500},
    ]

    def tick(self):
        """Return the tick data."""
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage['duration']:
                tick_data = (stage['users'], stage['spawn_rate'])
                return tick_data
        return None
