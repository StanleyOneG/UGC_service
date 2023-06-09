set -e
clickhouse client -n <<-EOSQL
  CREATE TABLE IF NOT EXISTS progress_queue (
    id String,
    user_movie_id String,
    timestamp UInt64)
    ENGINE = Kafka
    SETTINGS kafka_broker_list = '${KAFKA_HOST}:9092',
      kafka_topic_list = '${KAFKA_TOPIC}',
      kafka_format = 'JSONEachRow',
      kafka_num_consumers = 1,
      kafka_group_name = 'movie_progress_consumer_group';
EOSQL
