"""Average price endpoints (5-minute and 1-hour)."""

from typing import Any

from osrs_prices.endpoints.base import BaseEndpoint
from osrs_prices.models.prices import AverageResponse


class FiveMinuteEndpoint(BaseEndpoint[AverageResponse]):
    """Endpoint for fetching 5-minute average prices."""

    path = "/5m"

    def _parse_response(self, data: Any) -> AverageResponse:
        """Parse the API response into an AverageResponse."""
        return AverageResponse.from_api(data)

    def fetch(self, timestamp: int | None = None) -> AverageResponse:
        """Fetch 5-minute average prices.

        Args:
            timestamp: Optional Unix timestamp to get historical data.
                      If not provided, returns the latest data.

        Returns:
            The average price data.
        """
        params = {"timestamp": str(timestamp)} if timestamp is not None else None
        return self._request(params)


class OneHourEndpoint(BaseEndpoint[AverageResponse]):
    """Endpoint for fetching 1-hour average prices."""

    path = "/1h"

    def _parse_response(self, data: Any) -> AverageResponse:
        """Parse the API response into an AverageResponse."""
        return AverageResponse.from_api(data)

    def fetch(self, timestamp: int | None = None) -> AverageResponse:
        """Fetch 1-hour average prices.

        Args:
            timestamp: Optional Unix timestamp to get historical data.
                      If not provided, returns the latest data.

        Returns:
            The average price data.
        """
        params = {"timestamp": str(timestamp)} if timestamp is not None else None
        return self._request(params)
