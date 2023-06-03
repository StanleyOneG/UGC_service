"""Module for handling MongoDB connection and operations."""


from db.storage_interface import BaseStorage
from motor.motor_asyncio import AsyncIOMotorClient


class MongoStorage(BaseStorage):
    """Class for handling MongoDB connection and operations."""

    def __init__(self, database_name: str, collection_name: str):
        """Initialize MongoStorage class."""
        self._client = AsyncIOMotorClient('mongodb://mongos1,mongos2')
        self._database = self._client[database_name]
        self._collection = self._database[collection_name]

    async def get_data(self, *args, **kwargs) -> list:
        """Get data from MongoDB."""
        cursor = self._collection.find(*args, **kwargs)
        data = await cursor.to_list(length=None)
        return data

    async def create_data(self, *args, **kwargs) -> dict:
        """Create data in MongoDB."""
        return await self._collection.insert_one(*args, **kwargs)

    async def update_data(self, *args, **kwargs) -> dict:
        """Update data in MongoDB."""
        return await self._collection.update_one(*args, **kwargs)

    async def delete_data(self, *args, **kwargs) -> dict:
        """Delete data from MongoDB."""
        return await self._collection.delete_one(*args, **kwargs)
