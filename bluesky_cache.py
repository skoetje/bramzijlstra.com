import os
import json
import time
import hashlib
from typing import Dict, Any, Optional


class BlueskyCache:
    """Simple file-based cache for Bluesky comments."""

    def __init__(self, cache_dir: str = "cache", ttl_seconds: int = 3600):
        """
        Initialize the cache system.

        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds

        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key from a Bluesky URL."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _get_cache_path(self, key: str) -> str:
        """Get the file path for a cache key."""
        return os.path.join(self.cache_dir, f"{key}.json")

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached comments for a URL if they exist and aren't expired.

        Args:
            url: The Bluesky post URL

        Returns:
            Cached comments data or None if not in cache or expired
        """
        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cache_time = cache_data.get('timestamp', 0)
            current_time = time.time()

            if current_time - cache_time > self.ttl_seconds:
                # Cache expired
                return None

            return cache_data.get('data')

        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return None
            return None

    def set(self, url: str, data: Dict[str, Any]) -> None:
        """
        Store comments data in the cache.

        Args:
            url: The Bluesky post URL
            data: The comments data to cache
        """
        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        cache_data = {
            'timestamp': time.time(),
            'data': data
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except IOError:
            # If we can't write to the cache, just continue without caching
            pass

    def invalidate(self, url: str) -> None:
        """
        Remove a URL from the cache.

        Args:
            url: The Bluesky post URL to invalidate
        """
        key = self._get_cache_key(url)
        cache_path = self._get_cache_path(key)

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except IOError:
                pass