set -e

clickhouse client -n <<-EOSQL
    CREATE TABLE IF NOT EXISTS progress_queue (
        id Int32,
        user_movie_id String,
        timestamp UInt64) ENGINE = Kafka
        SETTINGS kafka_broker_list = 'kafka-1:9092',
            kafka_topic_list = 'movie_progress',
            kafka_format = 'JSONEachRow',
            kafka_group_name = 'movie_progress_consumer_group';
EOSQL