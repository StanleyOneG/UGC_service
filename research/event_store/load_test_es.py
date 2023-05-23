import logging
import random
import time
import uuid

from locust import HttpUser, LoadTestShape, between, events, task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventStoreLoadTest(HttpUser):
    """Load test for EventStore."""

    host = 'http://eventstore.db:2113'

    wait_time = between(1, 3)

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Event listener for user start event."""
        logger.info('TEST STARTED')

    @task
    def write_stream(self):
        """Task to simulate writing to a stream."""
        stream_name = 'my-stream'  # Replace with the name of your stream

        url = f'/streams/{stream_name}'

        message = '-'.join([str(uuid.uuid4()), str(random.randint(1, 1000000))])

        # random number of 8 digits for if
        event_id = str(uuid.uuid4())

        body = {'eventId': event_id, 'eventType': 'event-type', 'data': {'property': message}}
        headers = {'Content-Type': 'application/json', 'ES-EventType': body['eventType'], 'ES-EventId': body['eventId']}

        request_time_start = time.time()

        self.client.post(url, json=body, headers=headers)

        processing_time = int((time.time() - request_time_start) * 1000)

        events.request.fire(
            request_type='write_message',
            name='write_message',
            response_time=processing_time,
            response_length=0,
            context=None,
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
