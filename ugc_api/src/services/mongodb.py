"""Module for handling MongoDB connection and operations."""


from db.storage_interface import BaseStorage
from motor.motor_asyncio import AsyncIOMotorClient


class MongoStorage(BaseStorage):
    """Class for handling MongoDB connection and operations."""

    def __init__(self, storage_client: AsyncIOMotorClient, database_name: str, collection_name: str, **kwargs) -> None:
        """Initialize MongoStorage class."""
        self._client = storage_client
        self._database = self._client[database_name]
        self._collection = self._database[collection_name]

    async def get_data(self, *args, **kwargs) -> dict:
        """Get data from MongoDB."""
        return await self._collection.find(*args, **kwargs)

    async def set_data(self, *args, **kwargs) -> dict:
        """Insert data to MongoDB."""
        return await self._collection.insert_one(*args, **kwargs)

    async def delete_data(self, *args, **kwargs) -> dict:
        """Delete data from MongoDB."""
        return await self._collection.delete_one(*args, **kwargs)
