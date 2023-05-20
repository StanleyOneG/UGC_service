set -e
clickhouse client -n <<-EOSQL
  CREATE TABLE IF NOT EXISTS progress (
    id String,
    user_movie_id String,
    timestamp UInt64) Engine = MergeTree
      PARTITION BY user_movie_id
      ORDER BY id;
EOSQL
