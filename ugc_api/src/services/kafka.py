"""
Kafka service.

This module provides consumer and producer for Kafka messaging system.
"""

from core.config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC

from kafka import KafkaConsumer, KafkaProducer

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'],
    auto_offset_reset='earliest',
    group_id='echo-messages-to-stdout',
    api_version=(0, 10, 2),
)

producer = KafkaProducer(
    bootstrap_servers=[f'{KAFKA_HOST}:{KAFKA_PORT}'],
    api_version=(0, 10, 2),
)
