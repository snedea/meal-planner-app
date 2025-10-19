"""Redis caching utilities."""
import json
from typing import Any, Optional
import redis.asyncio as redis
from app.config import settings

# Create Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def cache_get(key: str) -> Optional[Any]:
    """
    Get value from cache.

    Args:
        key: Cache key

    Returns:
        Cached value or None if not found
    """
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in cache.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (default 1 hour)

    Returns:
        True if successful, False otherwise
    """
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """
    Delete value from cache.

    Args:
        key: Cache key

    Returns:
        True if successful, False otherwise
    """
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


async def cache_delete_pattern(pattern: str) -> bool:
    """
    Delete all keys matching pattern.

    Args:
        pattern: Key pattern (e.g., "food_*")

    Returns:
        True if successful, False otherwise
    """
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
        return False
