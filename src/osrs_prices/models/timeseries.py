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

    data: list[TimeseriesDataPoint] = Field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "TimeseriesResponse":
        """Create a TimeseriesResponse from API data.

        The API returns {"data": [{...}, ...]}.
        """
        points = [
            TimeseriesDataPoint.model_validate(point) for point in data.get("data", [])
        ]
        return cls(data=points)
