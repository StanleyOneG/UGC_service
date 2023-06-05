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
            (film_id UUID, user_id UUID, rating Nullable(Int32), bookmark UInt8, review_body String, review_date String)
            ENGINE = MergeTree() ORDER BY (film_id, user_id)"""
        )
    except Exception as e:
        logger.error(f'Error creating table "ugc_data": {e}')

    # create 'last_exc_timestamp' collection if it does not exist in MongoDB
    if 'last_exc_timestamp' not in mongo_client[mongo_database].list_collection_names():
        etl_time_collection = mongo_client[mongo_database]['last_exc_timestamp']
        etl_time_collection.insert_one({'timestamp': datetime.datetime(1970, 1, 1, 1)})
        logger.info('Collection "last_exc_timestamp" created')

    last_execution = mongo_client[mongo_database]['last_exc_timestamp'].find_one()
    logger.info('LAST_EXC_TIMESTAMP: %s', last_execution)
    if not last_execution:
        etl_time_collection.insert_one({'timestamp': datetime.datetime(1970, 1, 1, 1)})
        logger.info('No timestamp found in "last_exc_timestamp" collection')

    last_execution_timestamp = last_execution.get('timestamp')
    logger.info('LAST EXECUTION TIMESTAMP: %s', last_execution_timestamp)

    while True:
        try:
            # Query MongoDB for modified or created documents since the last execution
            query = {'last_modified': {'$gt': last_execution_timestamp}}
            modified_documents = list(ugc_collection.find(query))
            logger.info('MODIFIED_DOCUMENTS: %s', modified_documents)

            for mongo_doc in modified_documents:
                review_data = mongo_doc.get('review')
                if review_data is not None:
                    review = Review.parse_obj(review_data)
                else:
                    review = None

                ugc = dict(
                    film_id=uuid.UUID(bytes=mongo_doc.get('film_id')),
                    user_id=uuid.UUID(bytes=mongo_doc.get('user_id')),
                    rating=mongo_doc.get('rating'),
                    bookmark=mongo_doc.get('bookmark'),
                    review_body=review.review_body if review is not None else '',
                    review_date=str(review.review_date) if review is not None else None,
                )
                logger.info('review_date: %s', ugc.get('review_date'))

                # Replace 'None' values with None
                for key, value in ugc.items():
                    if value is None:
                        if key == 'rating':
                            ugc[key] = 0
                        elif key == 'review_date':
                            ugc[key] = ''
                        else:
                            ugc[key] = 'NULL'

                try:
                    # Check if the unique pair of film_id and user_id exists in ClickHouse
                    existing_data = clickhouse_client.execute(
                        'SELECT 1 FROM ugc_data WHERE film_id = %(film_id)s AND user_id = %(user_id)s LIMIT 1',
                        {'film_id': str(ugc['film_id']), 'user_id': str(ugc['user_id'])},
                    )
                    if existing_data:
                        # Update the existing record in ClickHouse
                        clickhouse_client.execute(
                            f"""ALTER TABLE ugc_data UPDATE
                            rating = {ugc["rating"]},
                            bookmark = {ugc["bookmark"]},
                            review_body = '{ugc["review_body"]}',
                            review_date = '{ugc["review_date"]}'
                            WHERE film_id = %(film_id)s AND user_id = %(user_id)s""",
                            {
                                'film_id': str(ugc['film_id']),
                                'user_id': str(ugc['user_id']),
                            },
                        )
                        logger.info('Data updated in table "ugc_data": %s', ugc)
                    else:
                        # Insert a new record in ClickHouse
                        clickhouse_client.execute(
                            'INSERT INTO ugc_data (film_id, user_id, rating, bookmark, review_body, review_date) VALUES',
                            [ugc],
                            types_check=True,
                        )
                        logger.info('Data inserted into table "ugc_data": %s', ugc)

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
                    logger.error(f'Error processing document: {mongo_doc}, Error: {e}')

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
            frequency=settings.app_settings.mongo_click_etl_frequency,
        )

    except Exception as e:
        logger.error(f'An error occurred: {e}')
