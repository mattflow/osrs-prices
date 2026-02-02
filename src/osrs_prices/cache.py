"""Thread-safe TTL cache implementation."""

import threading
import time
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """A simple thread-safe cache with time-to-live expiration."""

    def __init__(self, ttl: float) -> None:
        """Initialize the cache.

        Args:
            ttl: Time-to-live in seconds for cached values.
        """
        self._ttl = ttl
        self._value: T | None = None
        self._expiry: float = 0.0
        self._lock = threading.Lock()

    def get(self) -> T | None:
        """Get the cached value if it exists and hasn't expired.

        Returns:
            The cached value, or None if expired or not set.
        """
        with self._lock:
            if self._value is not None and time.monotonic() < self._expiry:
                return self._value
            return None

    def set(self, value: T) -> None:
        """Set a value in the cache.

        Args:
            value: The value to cache.
        """
        with self._lock:
            self._value = value
            self._expiry = time.monotonic() + self._ttl

    def invalidate(self) -> None:
        """Manually invalidate the cache."""
        with self._lock:
            self._value = None
            self._expiry = 0.0

    @property
    def ttl(self) -> float:
        """Return the TTL setting."""
        return self._ttl
