"""Item mapping endpoint with caching."""

from typing import Any

from osrs_prices.cache import TTLCache
from osrs_prices.constants import DEFAULT_CACHE_TTL
from osrs_prices.endpoints.base import BaseEndpoint
from osrs_prices.models.items import MappingResponse


class MappingEndpoint(BaseEndpoint[MappingResponse]):
    """Endpoint for fetching item mapping data with caching."""

    path = "/mapping"

    def __init__(self, client: Any, cache_ttl: float = DEFAULT_CACHE_TTL) -> None:
        """Initialize the mapping endpoint.

        Args:
            client: The httpx client to use for requests.
            cache_ttl: Time-to-live for the cache in seconds.
        """
        super().__init__(client)
        self._cache: TTLCache[MappingResponse] = TTLCache(cache_ttl)

    def _parse_response(self, data: Any) -> MappingResponse:
        """Parse the API response into a MappingResponse."""
        return MappingResponse.from_list(data)

    def fetch(self, force_refresh: bool = False) -> MappingResponse:
        """Fetch item mapping data.

        Args:
            force_refresh: If True, bypass the cache and fetch fresh data.

        Returns:
            The item mapping data.
        """
        if not force_refresh:
            cached = self._cache.get()
            if cached is not None:
                return cached

        response = self._request()
        self._cache.set(response)
        return response

    def invalidate_cache(self) -> None:
        """Manually invalidate the mapping cache."""
        self._cache.invalidate()
