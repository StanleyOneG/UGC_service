from confluent_kafka import Producer

# Kafka broker configuration
conf = {
    'bootstrap.servers': 'kafka-1:29092',
}


def get_kafka_producer(conf: dict = conf):
    """Create Kafka producer."""
    producer = Producer(conf)
    return producer
