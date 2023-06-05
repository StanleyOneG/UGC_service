"""Module for handling etl process of data transfer from MongoDB to ClickHouse."""

import datetime
import logging
import uuid
from time import sleep

import pytz
from clickhouse_driver import Client as ClickHouseClient
from config import Settings
from pymongo import MongoClient
from ugc_model import Review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    ugc_collection = mongo_client[mongo_database][mongo_collection]
    try:
        clickhouse_client.execute(
            """CREATE TABLE IF NOT EXISTS ugc_data
            (film_id UUID, user_id UUID, rating Nullable(Int32), bookmark UInt8, review_body String, review_date Nullable(DateTime))
            ENGINE = MergeTree() ORDER BY (film_id, user_id)"""
        )
        logger.info('Table "ugc_data" created')
    except Exception as e:
        logger.error(f'Error creating table "ugc_data": {e}')

    # create 'last_exc_timestamp' collection if it does not exist in MongoDB
    if 'last_exc_timestamp' not in mongo_client[mongo_database].list_collection_names():
        etl_time_collection = mongo_client[mongo_database]['last_exc_timestamp']
        etl_time_collection.insert_one({'timestamp': 0})
        logger.info('Collection "last_exc_timestamp" created')

    last_execution = mongo_client[mongo_database]['last_exc_timestamp'].find_one()
    logger.info('TIMESTAMP: %s', last_execution)
    if not last_execution:
        etl_time_collection.insert_one({'timestamp': 0})
        logger.info('No timestamp found in "last_exc_timestamp" collection')

    logger.info('BEFORE LAST EXC TIMESTAMP FETCH')
    last_execution_timestamp = last_execution.get('timestamp')
    logger.info('LAST EXECUTION TIMESTAMP: %s', last_execution_timestamp)

    while True:
        logger.info('INSIDE WHILE LOOP')
        try:
            # Query MongoDB for modified or created documents since the last execution
            query = {'last_modified': {'$gt': last_execution_timestamp}}
            logger.info('QUERY: %s', query)
            modified_documents = ugc_collection.find(query)

            clickhouse_data = []
            for mongo_doc in list(modified_documents):
                logger.info('MONGO_DOC: %s', mongo_doc)
                review_data = mongo_doc.get('review')
                logger.info('REVIEW_DATA: %s', review_data)
                if review_data is not None:
                    review = Review.dict()
                review = None

                ugc = dict(
                    film_id=uuid.UUID(bytes=mongo_doc.get('film_id')),
                    user_id=uuid.UUID(bytes=mongo_doc.get('user_id')),
                    rating=mongo_doc.get('rating'),
                    bookmark=mongo_doc.get('bookmark'),
                    review_body=review.review_body if review is not None else None,
                    review_date=review.review_date if review is not None else None,
                )

                # Replace 'None' values with None
                for key, value in ugc.items():
                    if value is None:
                        if key == 'rating':
                            ugc[key] = 0
                        elif key == 'review_date':
                            ugc[key] = 0
                        else:
                            ugc[key] = 'NULL'

                clickhouse_data.append(ugc)

            if clickhouse_data:
                logger.info('CLICKHOUSE_DATA: %s', clickhouse_data)
                try:
                    clickhouse_client.execute(
                        'INSERT INTO ugc_data (film_id, user_id, rating, bookmark, review_body, review_date) VALUES',
                        clickhouse_data,
                        types_check=True,
                    )
                    logger.info('Data inserted into table "ugc_data": %s', clickhouse_data)
                    # update 'last_exc_timestamp' collection to set timestamp now
                    mongo_client[mongo_database]['last_exc_timestamp'].update_one(
                        {},
                        {
                            '$set': {
                                'timestamp': datetime.datetime.now(pytz.utc),
                            }
                        },
                    )
                    logger.info('Timestamp updated in "last_exc_timestamp" collection')
                except Exception as e:
                    logger.error(f'Error inserting data into table "ugc_data": {e}')

            logger.info(f'Next iteration in {frequency} minutes.')
            sleep(frequency * 60)

        except Exception as pipeline_error:
            logger.error(f'An error occurred: {pipeline_error}')
            sleep(10)


if __name__ == '__main__':
    try:
        mongo_client = create_mongo_client()
        clickhouse_client = create_clickhouse_client()

        mongo_to_clickhouse(
            mongo_client=mongo_client,
            mongo_database=settings.mongodb.database_name,
            mongo_collection=settings.mongodb.collection_name,
            clickhouse_client=clickhouse_client,
            frequency=3,
        )

    except Exception as e:
        logger.error(f'An error occurred: {e}')
