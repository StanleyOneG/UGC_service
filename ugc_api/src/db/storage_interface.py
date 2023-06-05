"""Module describing abstract interface for a storage."""

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Abstract interface for a storage."""

    @abstractmethod
    async def get_data(self, *args, **kwargs) -> str:
        """
        Get data from storage.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str
        """
        pass

    @abstractmethod
    async def create_data(self, *args, **kwargs) -> None:
        """Create data in storage.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        pass

    @abstractmethod
    async def update_data(self, *args, **kwargs) -> None:
        """Update data in storage.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        pass

    @abstractmethod
    async def delete_data(self, *args, **kwargs) -> None:
        """Delete data from storage.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Nothing.
        """
        pass

    # @abstractmethod
    # async def aggregate_data(self, *args, **kwargs) -> str:
    #     """Aggregate data from storage."""
    #     pass
