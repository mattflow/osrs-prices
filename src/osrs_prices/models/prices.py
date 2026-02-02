"""Models for price data."""

from typing import Any

from pydantic import Field

from osrs_prices.models.base import OSRSBaseModel


class LatestPrice(OSRSBaseModel):
    """Current instant-buy and instant-sell prices for an item."""

    high: int | None = None
    high_time: int | None = Field(default=None, alias="highTime")
    low: int | None = None
    low_time: int | None = Field(default=None, alias="lowTime")


class LatestResponse(OSRSBaseModel):
    """Response from the /latest endpoint."""

    data: dict[int, LatestPrice] = Field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "LatestResponse":
        """Create a LatestResponse from API data.

        The API returns {"data": {"item_id": {...}, ...}}.
        Item IDs are strings in the JSON but we convert to int.
        """
        prices = {
            int(item_id): LatestPrice.model_validate(price_data)
            for item_id, price_data in data.get("data", {}).items()
        }
        return cls(data=prices)


class AveragePrice(OSRSBaseModel):
    """Average price data over a time period (5-minute or 1-hour)."""

    avg_high_price: int | None = Field(default=None, alias="avgHighPrice")
    high_price_volume: int | None = Field(default=None, alias="highPriceVolume")
    avg_low_price: int | None = Field(default=None, alias="avgLowPrice")
    low_price_volume: int | None = Field(default=None, alias="lowPriceVolume")


class AverageResponse(OSRSBaseModel):
    """Response from the /5m or /1h endpoints."""

    data: dict[int, AveragePrice] = Field(default_factory=dict)
    timestamp: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "AverageResponse":
        """Create an AverageResponse from API data.

        The API returns {"data": {"item_id": {...}, ...}, "timestamp": ...}.
        """
        prices = {
            int(item_id): AveragePrice.model_validate(price_data)
            for item_id, price_data in data.get("data", {}).items()
        }
        return cls(data=prices, timestamp=data.get("timestamp", 0))
