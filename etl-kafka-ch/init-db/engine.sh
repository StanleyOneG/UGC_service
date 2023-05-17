set -e
clickhouse client -n <<-EOSQL
  CREATE TABLE IF NOT EXISTS progress_queue (
    id Int32,
    user_movie_id String,
    timestamp UInt64)
    ENGINE = Kafka
    SETTINGS kafka_broker_list = 'broker:9092',
      kafka_topic_list = 'movie_progress',
      kafka_format = 'JSONEachRow',
      kafka_num_consumers = 1,
      kafka_group_name = 'movie_progress_consumer_group';
EOSQL