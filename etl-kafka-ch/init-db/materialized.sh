set -e
clickhouse client -n <<-EOSQL
  CREATE MATERIALIZED VIEW IF NOT EXISTS progress_queue_mv TO progress AS
  SELECT *
  FROM progress_queue;
EOSQL
