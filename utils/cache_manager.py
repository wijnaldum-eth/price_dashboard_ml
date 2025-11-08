"""
Cache manager with Redis backend and in-memory fallback.
Provides smart caching with configurable TTL and statistics tracking.
"""

import redis
import pickle
import logging
import functools
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import time

from config.settings import settings
from utils.exceptions import CacheError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching with Redis backend and in-memory fallback."""
    
    def __init__(self):
        """Initialize cache manager with Redis connection."""
        self.redis_client = None
        self.in_memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
        self._connect_redis()
    
    def _connect_redis(self):
        """Establish connection to Redis server."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,  # We'll handle encoding/decoding
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache as fallback.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    value = self.redis_client.get(key)
                    if value is not None:
                        self.cache_stats['hits'] += 1
                        return pickle.loads(value)
                except Exception as e:
                    logger.error(f"Redis get error: {e}")
                    self.cache_stats['errors'] += 1
            
            # Fallback to in-memory cache
            if key in self.in_memory_cache:
                entry = self.in_memory_cache[key]
                if entry['expires_at'] > datetime.now():
                    self.cache_stats['hits'] += 1
                    return entry['value']
                else:
                    # Expired, remove it
                    del self.in_memory_cache[key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.cache_stats['errors'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    serialized = pickle.dumps(value)
                    self.redis_client.setex(key, ttl, serialized)
                    return
                except Exception as e:
                    logger.error(f"Redis set error: {e}")
                    self.cache_stats['errors'] += 1
            
            # Fallback to in-memory cache
            self.in_memory_cache[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl)
            }
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.cache_stats['errors'] += 1
    
    def delete(self, key: str):
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        try:
            if self.redis_client:
                try:
                    self.redis_client.delete(key)
                except Exception as e:
                    logger.error(f"Redis delete error: {e}")
            
            if key in self.in_memory_cache:
                del self.in_memory_cache[key]
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
    def clear(self, pattern: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match keys (e.g., "prices:*")
                    If None, clears all cache
        """
        try:
            if self.redis_client:
                try:
                    if pattern:
                        keys = self.redis_client.keys(pattern)
                        if keys:
                            self.redis_client.delete(*keys)
                    else:
                        self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")
            
            # Clear in-memory cache
            if pattern:
                keys_to_delete = [k for k in self.in_memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self.in_memory_cache[key]
            else:
                self.in_memory_cache.clear()
                
            logger.info(f"Cache cleared{' with pattern: ' + pattern if pattern else ''}")
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache hit/miss/error counts and hit rate
        """
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'errors': self.cache_stats['errors'],
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests
        }
    
    def reset_stats(self):
        """Reset cache statistics."""
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if self.redis_client:
            try:
                self.redis_client.ping()
                return True
            except Exception:
                return False
        return False


# Create singleton instance
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @cached(ttl=120, key_prefix="prices")
        def get_prices(coin_id):
            return fetch_prices(coin_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}, executing function")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_with_refresh(ttl: int = 300, key_prefix: str = "", force_refresh: bool = False):
    """
    Decorator for caching with manual refresh option.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        force_refresh: If True, bypass cache and fetch fresh data
        
    Usage:
        @cache_with_refresh(ttl=120, key_prefix="prices")
        def get_prices(coin_id, force_refresh=False):
            return fetch_prices(coin_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, force_refresh=False, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            # Exclude force_refresh from cache key
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items()) if k != 'force_refresh'])
            cache_key = ":".join(filter(None, key_parts))
            
            # If force refresh, delete cache and fetch fresh
            if force_refresh:
                logger.debug(f"Force refresh for {cache_key}")
                cache_manager.delete(cache_key)
            else:
                # Try to get from cache
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_value
            
            # Execute function and cache result
            logger.debug(f"Fetching fresh data for {cache_key}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
