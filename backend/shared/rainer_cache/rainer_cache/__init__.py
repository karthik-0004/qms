"""Rainer Cache — Shared Redis caching for all Rainer Platform services."""

from rainer_cache.client import RedisCache, get_redis, close_redis

__version__ = "0.1.0"

__all__ = [
    "RedisCache",
    "get_redis",
    "close_redis",
]
