"""Models for timeseries data."""

from typing import Any, Literal

from pydantic import Field

from osrs_prices.models.base import OSRSBaseModel

Timestep = Literal["5m", "1h", "6h", "24h"]


class TimeseriesDataPoint(OSRSBaseModel):
    """A single data point in a timeseries."""

    timestamp: int
    avg_high_price: int | None = Field(default=None, alias="avgHighPrice")
    avg_low_price: int | None = Field(default=None, alias="avgLowPrice")
    high_price_volume: int | None = Field(default=None, alias="highPriceVolume")
    low_price_volume: int | None = Field(default=None, alias="lowPriceVolume")


class TimeseriesResponse(OSRSBaseModel):
    """Response from the /timeseries endpoint."""

    item_id: int | None = None
    data: list[TimeseriesDataPoint] = Field(default_factory=list)

    @classmethod
    def from_api(
        cls, data: dict[str, Any], item_id: int | None = None
    ) -> "TimeseriesResponse":
        """Create a TimeseriesResponse from API data.

        The API returns {"data": [{...}, ...]}.

        Args:
            data: The raw API response data.
            item_id: The item ID this timeseries is for.
        """
        points = [
            TimeseriesDataPoint.model_validate(point) for point in data.get("data", [])
        ]
        return cls(item_id=item_id, data=points)
