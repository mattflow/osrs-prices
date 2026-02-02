"""Main OSRS Prices API client."""

from typing import overload

from types import TracebackType

import httpx

from osrs_prices.constants import BLOCKED_USER_AGENTS, DEFAULT_CACHE_TTL, DEFAULT_TIMEOUT
from osrs_prices.endpoints.averages import FiveMinuteEndpoint, OneHourEndpoint
from osrs_prices.endpoints.latest import LatestEndpoint
from osrs_prices.endpoints.mapping import MappingEndpoint
from osrs_prices.endpoints.timeseries import TimeseriesEndpoint
from osrs_prices.exceptions import ValidationError
from osrs_prices.models.enriched import (
    EnrichedAveragePrice,
    EnrichedAverageResponse,
    EnrichedLatestPrice,
    EnrichedLatestResponse,
    EnrichedTimeseriesResponse,
)
from osrs_prices.models.items import ItemMapping, MappingResponse
from osrs_prices.models.prices import AverageResponse, LatestResponse
from osrs_prices.models.timeseries import Timestep, TimeseriesResponse


class Client:
    """Client for the OSRS Real-time Prices API.

    This client provides access to all OSRS Prices API endpoints with
    automatic caching for mapping data and proper User-Agent handling.

    Example:
        >>> with Client(user_agent="my-app/1.0") as client:
        ...     mapping = client.get_mapping()
        ...     prices = client.get_latest()
    """

    def __init__(
        self,
        user_agent: str,
        timeout: float = DEFAULT_TIMEOUT,
        cache_ttl: float = DEFAULT_CACHE_TTL,
    ) -> None:
        """Initialize the client.

        Args:
            user_agent: A descriptive User-Agent string identifying your application.
                       Must not be a generic library agent (e.g., "python-requests").
            timeout: Request timeout in seconds.
            cache_ttl: Time-to-live for the mapping cache in seconds.

        Raises:
            ValidationError: If the user_agent is invalid or blocked.
        """
        self._validate_user_agent(user_agent)

        self._http_client = httpx.Client(
            headers={"User-Agent": user_agent},
            timeout=timeout,
        )

        self._latest = LatestEndpoint(self._http_client)
        self._mapping = MappingEndpoint(self._http_client, cache_ttl=cache_ttl)
        self._five_minute = FiveMinuteEndpoint(self._http_client)
        self._one_hour = OneHourEndpoint(self._http_client)
        self._timeseries = TimeseriesEndpoint(self._http_client)

        self._name_to_id_cache: dict[str, int] | None = None

    def _validate_user_agent(self, user_agent: str) -> None:
        """Validate that the user agent is acceptable.

        Args:
            user_agent: The user agent string to validate.

        Raises:
            ValidationError: If the user agent is invalid.
        """
        if not user_agent or not user_agent.strip():
            raise ValidationError("User-Agent must not be empty")

        user_agent_lower = user_agent.lower()
        for blocked in BLOCKED_USER_AGENTS:
            if blocked in user_agent_lower:
                raise ValidationError(
                    f"User-Agent must not contain blocked agent: {blocked}. "
                    "Please use a descriptive agent like 'my-app/1.0 contact@example.com'"
                )

    def __enter__(self) -> "Client":
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the HTTP client."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._http_client.close()

    def get_latest(self, item_id: int | None = None) -> LatestResponse:
        """Get the latest instant-buy and instant-sell prices.

        Args:
            item_id: Optional item ID to filter to a single item.

        Returns:
            The latest price data.
        """
        return self._latest.fetch(item_id)

    def get_mapping(self, force_refresh: bool = False) -> MappingResponse:
        """Get item mapping data (metadata for all items).

        This data is cached by default. Use force_refresh to bypass the cache.

        Args:
            force_refresh: If True, bypass the cache and fetch fresh data.

        Returns:
            The item mapping data.
        """
        return self._mapping.fetch(force_refresh)

    def get_5m_average(self, timestamp: int | None = None) -> AverageResponse:
        """Get 5-minute average prices.

        Args:
            timestamp: Optional Unix timestamp to get historical data.
                      If not provided, returns the latest data.

        Returns:
            The 5-minute average price data.
        """
        return self._five_minute.fetch(timestamp)

    def get_1h_average(self, timestamp: int | None = None) -> AverageResponse:
        """Get 1-hour average prices.

        Args:
            timestamp: Optional Unix timestamp to get historical data.
                      If not provided, returns the latest data.

        Returns:
            The 1-hour average price data.
        """
        return self._one_hour.fetch(timestamp)

    def get_timeseries(self, item_id: int, timestep: Timestep) -> TimeseriesResponse:
        """Get historical timeseries data for an item.

        Args:
            item_id: The item ID to fetch data for.
            timestep: The time interval for data points ("5m", "1h", "6h", or "24h").

        Returns:
            The timeseries data.
        """
        return self._timeseries.fetch(item_id, timestep)

    def invalidate_mapping_cache(self) -> None:
        """Manually invalidate the mapping cache."""
        self._mapping.invalidate_cache()
        self._name_to_id_cache = None

    def get_item_by_name(self, name: str) -> ItemMapping | None:
        """Find an item by its exact name.

        Args:
            name: The exact item name to search for.

        Returns:
            The item mapping if found, None otherwise.
        """
        if self._name_to_id_cache is None:
            mapping = self.get_mapping()
            self._name_to_id_cache = {item.name: item.id for item in mapping.items}

        item_id = self._name_to_id_cache.get(name)
        if item_id is None:
            return None

        mapping = self.get_mapping()
        for item in mapping.items:
            if item.id == item_id:
                return item
        return None

    def _build_mapping_lookup(self) -> dict[int, ItemMapping]:
        """Build a lookup dictionary from item ID to ItemMapping.

        Returns:
            Dictionary mapping item IDs to their ItemMapping objects.
        """
        mapping = self.get_mapping()
        return {item.id: item for item in mapping.items}

    def get_latest_with_mapping(
        self, item_id: int | None = None
    ) -> EnrichedLatestResponse:
        """Get latest prices enriched with item metadata.

        Args:
            item_id: Optional item ID to filter to a single item.

        Returns:
            Latest prices combined with item mapping data.

        Example:
            >>> with Client(user_agent="my-app/1.0") as client:
            ...     enriched = client.get_latest_with_mapping()
            ...     for item in enriched.items:
            ...         print(f"{item.name}: {item.high} gp")
        """
        latest = self.get_latest(item_id)
        return self._enrich_latest_response(latest)

    def get_5m_average_with_mapping(
        self, timestamp: int | None = None
    ) -> EnrichedAverageResponse:
        """Get 5-minute average prices enriched with item metadata.

        Args:
            timestamp: Optional Unix timestamp to get historical data.

        Returns:
            5-minute average prices combined with item mapping data.
        """
        averages = self.get_5m_average(timestamp)
        return self._enrich_average_response(averages)

    def get_1h_average_with_mapping(
        self, timestamp: int | None = None
    ) -> EnrichedAverageResponse:
        """Get 1-hour average prices enriched with item metadata.

        Args:
            timestamp: Optional Unix timestamp to get historical data.

        Returns:
            1-hour average prices combined with item mapping data.
        """
        averages = self.get_1h_average(timestamp)
        return self._enrich_average_response(averages)

    def _enrich_latest_response(
        self, latest: LatestResponse
    ) -> EnrichedLatestResponse:
        """Enrich a LatestResponse with item metadata.

        Args:
            latest: The latest response to enrich.

        Returns:
            Enriched latest response with item metadata.
        """
        lookup = self._build_mapping_lookup()

        items = []
        for item_id, price in latest.data.items():
            mapping_item = lookup.get(item_id)
            if mapping_item is not None:
                items.append(
                    EnrichedLatestPrice(
                        id=mapping_item.id,
                        name=mapping_item.name,
                        examine=mapping_item.examine,
                        members=mapping_item.members,
                        lowalch=mapping_item.lowalch,
                        highalch=mapping_item.highalch,
                        limit=mapping_item.limit,
                        value=mapping_item.value,
                        icon=mapping_item.icon,
                        high=price.high,
                        high_time=price.high_time,
                        low=price.low,
                        low_time=price.low_time,
                    )
                )

        return EnrichedLatestResponse(items=items)

    def _enrich_average_response(
        self, averages: AverageResponse
    ) -> EnrichedAverageResponse:
        """Enrich an AverageResponse with item metadata.

        Args:
            averages: The average response to enrich.

        Returns:
            Enriched average response with item metadata.
        """
        lookup = self._build_mapping_lookup()

        items = []
        for item_id, price in averages.data.items():
            mapping_item = lookup.get(item_id)
            if mapping_item is not None:
                items.append(
                    EnrichedAveragePrice(
                        id=mapping_item.id,
                        name=mapping_item.name,
                        examine=mapping_item.examine,
                        members=mapping_item.members,
                        lowalch=mapping_item.lowalch,
                        highalch=mapping_item.highalch,
                        limit=mapping_item.limit,
                        value=mapping_item.value,
                        icon=mapping_item.icon,
                        avg_high_price=price.avg_high_price,
                        high_price_volume=price.high_price_volume,
                        avg_low_price=price.avg_low_price,
                        low_price_volume=price.low_price_volume,
                    )
                )

        return EnrichedAverageResponse(items=items, timestamp=averages.timestamp)

    def get_timeseries_with_mapping(
        self, item_id: int, timestep: Timestep
    ) -> EnrichedTimeseriesResponse:
        """Get timeseries data with item metadata attached.

        Args:
            item_id: The item ID to fetch data for.
            timestep: The time interval for data points ("5m", "1h", "6h", or "24h").

        Returns:
            Timeseries data with the item's metadata.

        Raises:
            ValidationError: If the item_id is not found in the mapping.
        """
        timeseries = self.get_timeseries(item_id, timestep)
        lookup = self._build_mapping_lookup()

        mapping_item = lookup.get(item_id)
        if mapping_item is None:
            raise ValidationError(f"Item ID {item_id} not found in mapping")

        return EnrichedTimeseriesResponse(item=mapping_item, data=timeseries.data)

    @overload
    def enrich(self, response: LatestResponse) -> EnrichedLatestResponse: ...

    @overload
    def enrich(self, response: AverageResponse) -> EnrichedAverageResponse: ...

    def enrich(
        self, response: LatestResponse | AverageResponse
    ) -> EnrichedLatestResponse | EnrichedAverageResponse:
        """Enrich an existing response with item metadata.

        This is a convenience method for users who already have a response
        and want to add item metadata to it.

        Args:
            response: A LatestResponse or AverageResponse to enrich.

        Returns:
            The enriched response with item metadata added.

        Example:
            >>> with Client(user_agent="my-app/1.0") as client:
            ...     latest = client.get_latest()
            ...     enriched = client.enrich(latest)
            ...     for item in enriched.items:
            ...         print(f"{item.name}: {item.high} gp")
        """
        if isinstance(response, LatestResponse):
            return self._enrich_latest_response(response)
        else:
            return self._enrich_average_response(response)
