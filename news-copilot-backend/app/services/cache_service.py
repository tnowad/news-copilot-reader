from typing import Any, Optional, List, Dict, Callable
from functools import wraps
import json
import hashlib
from datetime import datetime, timedelta

from app.extensions import cache


class CacheService:
    """Enhanced caching service with advanced features"""
    
    DEFAULT_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return cache.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Set value in cache"""
        try:
            return cache.set(key, value, timeout=timeout)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            return cache.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            # This is a simple implementation - in production, use Redis with SCAN
            # For now, we'll implement a basic pattern matching
            deleted_count = 0
            # Note: flask-caching doesn't support pattern deletion by default
            # This would need Redis backend for full functionality
            return deleted_count
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def get_or_set(key: str, callable_func: Callable, timeout: int = DEFAULT_TIMEOUT) -> Any:
        """Get from cache or execute function and cache result"""
        try:
            value = CacheService.get(key)
            if value is not None:
                return value
            
            value = callable_func()
            CacheService.set(key, value, timeout)
            return value
        except Exception as e:
            print(f"Cache get_or_set error: {e}")
            # Fallback to executing function without caching
            return callable_func()


def cached_response(timeout: int = CacheService.DEFAULT_TIMEOUT, key_prefix: str = None):
    """Decorator for caching API responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = f"{key_prefix}:{CacheService.generate_key(*args, **kwargs)}"
            else:
                cache_key = f"{func.__name__}:{CacheService.generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheService.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_invalidate_on_change(cache_keys: List[str]):
    """Decorator to invalidate cache keys when function is called"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache keys
            for key in cache_keys:
                CacheService.delete(key)
            
            return result
        return wrapper
    return decorator


class ModelCacheManager:
    """Cache manager for database models"""
    
    @staticmethod
    def cache_model_result(model_name: str, method: str, *args, timeout: int = 3600, **kwargs):
        """Cache model query result"""
        cache_key = f"model:{model_name}:{method}:{CacheService.generate_key(*args, **kwargs)}"
        return cached_response(timeout=timeout, key_prefix=cache_key)
    
    @staticmethod
    def invalidate_model_cache(model_name: str, method: str = None):
        """Invalidate all cache for a model or specific method"""
        if method:
            pattern = f"model:{model_name}:{method}:*"
        else:
            pattern = f"model:{model_name}:*"
        
        return CacheService.delete_pattern(pattern)


# Specific cache managers for different resources
class ArticleCacheManager:
    """Cache manager specifically for articles"""
    
    CACHE_TIMEOUT = 1800  # 30 minutes
    
    @staticmethod
    def get_articles_key(filters: Dict[str, Any]) -> str:
        """Generate cache key for articles list"""
        return f"articles:list:{CacheService.generate_key(**filters)}"
    
    @staticmethod
    def get_article_key(article_id: int) -> str:
        """Generate cache key for single article"""
        return f"articles:detail:{article_id}"
    
    @staticmethod
    def get_trending_key(days: int, limit: int) -> str:
        """Generate cache key for trending articles"""
        return f"articles:trending:{days}:{limit}"
    
    @staticmethod
    def invalidate_article_caches(article_id: int = None):
        """Invalidate article-related caches"""
        if article_id:
            CacheService.delete(ArticleCacheManager.get_article_key(article_id))
        
        # Invalidate list caches (in production, use pattern deletion)
        CacheService.delete_pattern("articles:list:*")
        CacheService.delete_pattern("articles:trending:*")


class UserCacheManager:
    """Cache manager specifically for users"""
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def get_user_key(user_id: int) -> str:
        """Generate cache key for user"""
        return f"users:detail:{user_id}"
    
    @staticmethod
    def get_user_profile_key(user_id: int) -> str:
        """Generate cache key for user profile"""
        return f"users:profile:{user_id}"
    
    @staticmethod
    def get_user_stats_key(user_id: int) -> str:
        """Generate cache key for user statistics"""
        return f"users:stats:{user_id}"
    
    @staticmethod
    def invalidate_user_caches(user_id: int):
        """Invalidate user-related caches"""
        CacheService.delete(UserCacheManager.get_user_key(user_id))
        CacheService.delete(UserCacheManager.get_user_profile_key(user_id))
        CacheService.delete(UserCacheManager.get_user_stats_key(user_id))
