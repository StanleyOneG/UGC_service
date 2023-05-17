"""Module for load testing of Kafka."""

import json
import time

from confluent_kafka import Producer
from locust import HttpUser, between, events, task

topic = 'my_topic'


class KafkaLoadTest(HttpUser):
    """Test class for load testing of Kafka."""

    wait_time = between(1, 3)  # Wait time between consecutive tasks

    host = 'http://localhost:9092'

    @task
    def produce_messages(self):
        """Produce messages to Kafka and gather statistics."""
        # Kafka broker configuration
        conf = {
            'bootstrap.servers': 'localhost:9092',
        }

        # Create Kafka producer
        producer = Producer(conf)

        # Produce messages to Kafka
        message = {'key': 'value'}
        request_time_start = time.time()
        producer.produce(topic, value=json.dumps(message).encode('utf-8'))

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


if __name__ == '__main__':
    KafkaLoadTest().run()
