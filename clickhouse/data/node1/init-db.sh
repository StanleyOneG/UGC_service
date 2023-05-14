
set -e

echo ======== starting to create databases and tables ===============
clickhouse client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS shard;
    CREATE TABLE IF NOT EXISTS shard.progress (id Int64, user_movie_id String, timestamp UInt64) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/progress', 'replica_1') PARTITION BY user_movie_id ORDER BY id;
    CREATE TABLE IF NOT EXISTS default.progress (id Int64, user_movie_id String, timestamp UInt64) ENGINE=Distributed('company_cluster', '', progress, rand());
EOSQL
echo ==== database shard created. shard.progress, default.progress tables created ====