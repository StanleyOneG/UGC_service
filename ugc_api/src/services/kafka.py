"""
Kafka service.

This module provides consumer and producer for Kafka messaging system.
"""

from typing import Optional

from aiokafka import AIOKafkaProducer

producer: Optional[AIOKafkaProducer] = None


def get_producer() -> AIOKafkaProducer:
    """
    Retrieve the KafkaProducer instance.

    Returns:
        AIOKafkaProducer: The Kafka instance.
    """
    return producer
