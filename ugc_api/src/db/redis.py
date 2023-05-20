"""Redis connection."""

from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


def get_redis() -> Redis:
    """
    Retrieve the Redis instance.

    Returns:
        Redis: The Redis instance.
    """
    return redis
