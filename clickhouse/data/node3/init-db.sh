
set -e
echo ======== starting to create databases and tables ===============
clickhouse client -n <<-EOSQL
    CREATE DATABASE shard;
    CREATE TABLE shard.progress (id Int64, user_movie_id String, timestamp UInt64) Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/progress', 'replica_1') PARTITION BY user_movie_id ORDER BY id;
    CREATE TABLE default.progress (id Int64, user_movie_id String, timestamp UInt64) ENGINE = Distributed('company_cluster', '', progress, rand());
EOSQL
echo ==== database shard created. shard.progress, default.progress tables created ====