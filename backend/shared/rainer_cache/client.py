"""Async Redis cache client with cache-aside pattern, TTL, and namespacing."""

from __future__ import annotations

import json
from typing import Any

import structlog
from redis.asyncio import Redis, ConnectionPool

logger = structlog.get_logger(__name__)

_pool: ConnectionPool | None = None
_redis: Redis | None = None


async def get_redis(redis_url: str = "redis://localhost:6379/0") -> Redis:
    """Get or create a singleton async Redis connection."""
    global _pool, _redis
    if _redis is None:
        _pool = ConnectionPool.from_url(
            redis_url,
            max_connections=20,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
        )
        _redis = Redis(connection_pool=_pool)
        await _redis.ping()
        logger.info("redis_connected", url=redis_url)
    return _redis


async def close_redis() -> None:
    """Gracefully close the Redis connection pool."""
    global _pool, _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
    if _pool is not None:
        await _pool.disconnect()
        _pool = None
        logger.info("redis_disconnected")


class RedisCache:
    """High-level cache-aside helper with namespace, TTL, and JSON serialization."""

    def __init__(self, redis: Redis, namespace: str = "", default_ttl: int = 300):
        self._redis = redis
        self._namespace = namespace
        self._default_ttl = default_ttl

    def _key(self, key: str) -> str:
        return f"{self._namespace}:{key}" if self._namespace else key

    async def get(self, key: str) -> Any | None:
        """Get a cached value, returns None on miss."""
        raw = await self._redis.get(self._key(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a cached value with optional TTL override."""
        serialized = json.dumps(value, default=str)
        await self._redis.set(
            self._key(key),
            serialized,
            ex=ttl or self._default_ttl,
        )

    async def delete(self, key: str) -> None:
        """Delete a cached key."""
        await self._redis.delete(self._key(key))

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern within this namespace."""
        full_pattern = self._key(pattern)
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await self._redis.scan(cursor, match=full_pattern, count=100)
            if keys:
                deleted += await self._redis.delete(*keys)
            if cursor == 0:
                break
        logger.info("cache_invalidated", pattern=full_pattern, deleted=deleted)
        return deleted

    async def get_or_set(self, key: str, factory, ttl: int | None = None) -> Any:
        """Cache-aside: return cached value or call factory, cache result, and return."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await factory() if callable(factory) else factory
        await self.set(key, value, ttl)
        return value

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomic increment — useful for rate limiting counters."""
        return await self._redis.incrby(self._key(key), amount)

    async def expire(self, key: str, ttl: int) -> None:
        """Set expiration on an existing key."""
        await self._redis.expire(self._key(key), ttl)
