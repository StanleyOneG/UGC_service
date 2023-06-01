"""Module describing abstract interface for a storage."""

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Abstract interface for a storage."""

    @abstractmethod
    def get_data(self, *args, **kwargs) -> str:
        """Get data from storage."""
        pass

    @abstractmethod
    def set_data(self, *args, **kwargs) -> None:
        """Set data to storage."""
        pass

    @abstractmethod
    def delete_data(self, *args, **kwargs) -> None:
        """Delete data from storage."""
        pass
