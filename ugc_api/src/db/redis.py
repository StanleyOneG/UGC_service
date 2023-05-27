"""Redis connection."""

from typing import Optional, Any

from redis.asyncio import Redis

redis: Optional[Redis] = None


def get_redis() -> Optional[Redis]:
    """
    Retrieve the Redis instance.

    Returns:
        Redis: The Redis instance.
    """
    return redis
