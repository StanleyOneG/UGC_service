"""Module for creating a database instance."""

from db.storage_interface import BaseStorage

storage: BaseStorage = None


def get_storage() -> BaseStorage:
    """Return the database instance."""
    return storage
