"""Module for handling MongoDB connection and operations."""


from db.storage_interface import BaseStorage
from motor.motor_asyncio import AsyncIOMotorClient


class MongoStorage(BaseStorage):
    """Class for handling MongoDB connection and operations."""

    def __init__(self, database_name: str, collection_name: str):
        """Initialize MongoStorage class.

        Args:
            database_name: str
            collection_name: str
        """
        self._client = AsyncIOMotorClient('mongodb://mongos1,mongos2')
        self._database = self._client[database_name]
        self._collection = self._database[collection_name]

    async def get_data(self, *args, **kwargs) -> list:
        """Get data from MongoDB.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        cursor = self._collection.find(*args, **kwargs)
        return await cursor.to_list(length=None)

    async def create_data(self, *args, **kwargs) -> dict:
        """Create data in MongoDB.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        return await self._collection.insert_one(*args, **kwargs)

    async def update_data(self, *args, **kwargs) -> dict:
        """Update data in MongoDB.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        return await self._collection.update_one(*args, **kwargs)

    async def delete_data(self, *args, **kwargs) -> dict:
        """Delete data from MongoDB.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        return await self._collection.delete_one(*args, **kwargs)
