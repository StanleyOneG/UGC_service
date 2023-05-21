"""
Kafka service.

This module provides consumer and producer for Kafka messaging system.
"""

from kafka import KafkaConsumer, KafkaProducer
from core.config import KAFKA_TOPIC, KAFKA_HOST, KAFKA_PORT

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'],
    auto_offset_reset='earliest',
    group_id='echo-messages-to-stdout',
    api_version=(0, 10, 2),
)

producer = KafkaProducer(bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'],
                         api_version=(0, 10, 2),)
