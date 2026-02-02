"""Timeseries endpoint for historical price data."""

from typing import Any

from osrs_prices.endpoints.base import BaseEndpoint
from osrs_prices.models.timeseries import Timestep, TimeseriesResponse


class TimeseriesEndpoint(BaseEndpoint[TimeseriesResponse]):
    """Endpoint for fetching historical timeseries data."""

    path = "/timeseries"

    def __init__(self, http_client: Any) -> None:
        """Initialize the endpoint."""
        super().__init__(http_client)
        self._current_item_id: int | None = None

    def _parse_response(self, data: Any) -> TimeseriesResponse:
        """Parse the API response into a TimeseriesResponse."""
        return TimeseriesResponse.from_api(data, item_id=self._current_item_id)

    def fetch(self, item_id: int, timestep: Timestep) -> TimeseriesResponse:
        """Fetch historical timeseries data for an item.

        Args:
            item_id: The item ID to fetch data for.
            timestep: The time interval for data points ("5m", "1h", "6h", or "24h").

        Returns:
            The timeseries data.
        """
        self._current_item_id = item_id
        params = {"id": str(item_id), "timestep": timestep}
        return self._request(params)
