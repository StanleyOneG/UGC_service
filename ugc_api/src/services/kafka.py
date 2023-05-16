"""
Kafka service.

This module provides consumer and producer for Kafka messaging system.
"""


from kafka import KafkaConsumer, KafkaProducer

consumer = KafkaConsumer(
    'topic_ugc',
    bootstrap_servers=['0.0.0.0:9092'],
    auto_offset_reset='earliest',
    group_id='echo-messages-to-stdout',
)

# for message in consumer:
#     print(message.value)


producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

# producer.send(
#     topic='views',
#     value=b'1611039931',
#     key=b'500271+tt0120338',
# )
