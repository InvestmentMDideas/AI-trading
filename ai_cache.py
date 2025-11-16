"""
AI Response Cache
Speed optimization through response caching.
"""

import time
from typing import Optional, Dict, Any


class AICache:
    """Simple in-memory cache for AI responses."""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            ttl: Time to live in seconds (default 5 minutes)
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
        self.hits = 0
        self.misses = 0
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self.timestamps:
            return True
        age = time.time() - self.timestamps[key]
        return age > self.ttl
    
    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key (usually the prompt)
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self.cache and not self._is_expired(key):
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            # Remove expired entry
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
            return None
    
    def set(self, key: str, value: str):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Enforce max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest entry
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total,
            'hit_rate': round(hit_rate, 1),
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }


if __name__ == "__main__":
    # Quick test
    cache = AICache(max_size=5, ttl=2)
    
    cache.set("key1", "value1")
    print(f"Get key1: {cache.get('key1')}")  # Should work
    print(f"Get key2: {cache.get('key2')}")  # Should be None
    
    time.sleep(2.1)
    print(f"Get key1 after TTL: {cache.get('key1')}")  # Should be None (expired)
    
    print(f"Stats: {cache.get_stats()}")