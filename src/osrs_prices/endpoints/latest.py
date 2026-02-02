"""Latest prices endpoint."""

from typing import Any

from osrs_prices.endpoints.base import BaseEndpoint
from osrs_prices.models.prices import LatestResponse


class LatestEndpoint(BaseEndpoint[LatestResponse]):
    """Endpoint for fetching latest instant-buy/sell prices."""

    path = "/latest"

    def _parse_response(self, data: Any) -> LatestResponse:
        """Parse the API response into a LatestResponse."""
        return LatestResponse.from_api(data)

    def fetch(self, item_id: int | None = None) -> LatestResponse:
        """Fetch latest prices.

        Args:
            item_id: Optional item ID to filter results to a single item.

        Returns:
            The latest price data.
        """
        params = {"id": str(item_id)} if item_id is not None else None
        return self._request(params)
