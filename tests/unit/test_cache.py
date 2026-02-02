"""Unit tests for the TTL cache."""

import time

from osrs_prices.cache import TTLCache


class TestTTLCache:
    """Tests for TTLCache class."""

    def test_set_and_get(self) -> None:
        """Test basic set and get operations."""
        cache: TTLCache[str] = TTLCache(ttl=60.0)
        cache.set("test_value")
        assert cache.get() == "test_value"

    def test_get_empty_cache(self) -> None:
        """Test get on empty cache returns None."""
        cache: TTLCache[str] = TTLCache(ttl=60.0)
        assert cache.get() is None

    def test_expiry(self) -> None:
        """Test that cache expires after TTL."""
        cache: TTLCache[str] = TTLCache(ttl=0.05)  # 50ms TTL
        cache.set("test_value")
        assert cache.get() == "test_value"
        time.sleep(0.06)  # Wait for expiry
        assert cache.get() is None

    def test_invalidate(self) -> None:
        """Test manual cache invalidation."""
        cache: TTLCache[str] = TTLCache(ttl=60.0)
        cache.set("test_value")
        assert cache.get() == "test_value"
        cache.invalidate()
        assert cache.get() is None

    def test_overwrite(self) -> None:
        """Test that setting a new value overwrites the old one."""
        cache: TTLCache[str] = TTLCache(ttl=60.0)
        cache.set("value1")
        cache.set("value2")
        assert cache.get() == "value2"

    def test_ttl_property(self) -> None:
        """Test that ttl property returns the configured TTL."""
        cache: TTLCache[str] = TTLCache(ttl=3600.0)
        assert cache.ttl == 3600.0

    def test_complex_value(self) -> None:
        """Test caching complex objects."""
        cache: TTLCache[dict] = TTLCache(ttl=60.0)
        value = {"key": "value", "nested": {"a": 1}}
        cache.set(value)
        assert cache.get() == value
