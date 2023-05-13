
set -e

echo ======== starting to create databases and tables ===============
clickhouse client -n <<-EOSQL
    CREATE DATABASE replica;
    CREATE TABLE replica.progress (id Int64, user_movie_id String, timestamp UInt64) Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/progress', 'replica_2') PARTITION BY user_movie_id ORDER BY id;
EOSQL
echo ==== database replica created. replica.progress tables created ====