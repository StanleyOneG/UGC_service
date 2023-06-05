"""Module for handling etl process of data transfer from MongoDB to ClickHouse."""

from time import sleep

from clickhouse_driver import Client as ClickHouseClient
from pymongo import MongoClient

from ugc_api.src.core.config import Settings
from ugc_api.src.models.ugc_model import UGC, Review

settings = Settings()


def create_mongo_client():
    """Create a MongoDB client."""
    client = MongoClient(host='mongos1,mongos2')
    return client


def create_clickhouse_client():
    """Create a ClickHouse client."""
    client_ch = ClickHouseClient(host='clickhouse')
    return client_ch


def mongo_to_clickhouse(
    mongo_client: MongoClient,
    mongo_database: str,
    mongo_collection: str,
    clickhouse_client: ClickHouseClient,
    frequency: int,
):
    """
    ETL process of data transfer from MongoDB to ClickHouse.

    Args:
        mongo_client (MongoClient): MongoDB client.
        mongo_db (str): MongoDB database name.
        mongo_collection (str): MongoDB collection name.
        clickhouse_client (ClickHouseClient): ClickHouse client.
        frequency (int): Frequency of data transfer in minutes.
    """
    # create 'last_exc_timestamp' collection if it does not exist in MongoDB
    if 'last_exc_timestamp' not in mongo_client[mongo_database].collection_names():
        mongo_client[mongo_database].create_collection('last_exc_timestamp')

    last_execution_timestamp = mongo_client[mongo_database]['last_exc_timestamp'].find_one()['timestamp']

    while True:
        # Query MongoDB for modified or created documents since the last execution
        query = {'last_modified': {'$gt': last_execution_timestamp}}
        modified_documents = mongo_collection.find(query)

        clickhouse_data = []
        for mongo_doc in modified_documents:
            review_data = mongo_doc.get('review')
            review = Review.parse_obj(review_data) if review_data else None

            ugc = UGC(
                film_id=mongo_doc.get('film_id'),
                user_id=mongo_doc.get('user_id'),
                rating=mongo_doc.get('rating'),
                bookmark=mongo_doc.get('bookmark'),
                review=review,
            )
            clickhouse_data.append(ugc.dict())

        clickhouse_client.execute(
            """CREATE TABLE IF NOT EXISTS ugc_data
            (film_id UUID, user_id UUID, rating Nullable(Int32), bookmark UInt8, review_body String, review_date DateTime)
            ENGINE = MergeTree() ORDER BY (film_id, user_id)"""
        )

        clickhouse_client.execute(
            'INSERT INTO your_clickhouse_table (film_id, user_id, rating, bookmark, review_body, review_date) VALUES',
            clickhouse_data,
            types_check=True,
        )

        sleep(frequency * 60)


if __name__ == '__main__':
    mongo_client = create_mongo_client()
    clickhouse_client = create_clickhouse_client()

    mongo_to_clickhouse(
        mongo_client=mongo_client,
        mongo_database=settings.mongodb.database_name,
        mongo_collection=settings.mongodb.collection_name,
        clickhouse_client=clickhouse_client,
        frequency=3,
    )
