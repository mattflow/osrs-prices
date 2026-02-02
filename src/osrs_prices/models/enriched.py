"""Enriched models combining price data with item metadata."""

from osrs_prices.models.base import OSRSBaseModel
from osrs_prices.models.items import ItemMapping
from osrs_prices.models.timeseries import TimeseriesDataPoint


class EnrichedItemBase(OSRSBaseModel):
    """Base class with common item metadata fields."""

    id: int
    name: str
    examine: str | None = None
    members: bool
    lowalch: int | None = None
    highalch: int | None = None
    limit: int | None = None
    value: int | None = None
    icon: str


class EnrichedLatestPrice(EnrichedItemBase):
    """Latest price combined with item metadata."""

    high: int | None = None
    high_time: int | None = None
    low: int | None = None
    low_time: int | None = None


class EnrichedLatestResponse(OSRSBaseModel):
    """Response containing latest prices enriched with item metadata."""

    items: list[EnrichedLatestPrice]


class EnrichedAveragePrice(EnrichedItemBase):
    """Average price combined with item metadata."""

    avg_high_price: int | None = None
    high_price_volume: int | None = None
    avg_low_price: int | None = None
    low_price_volume: int | None = None


class EnrichedAverageResponse(OSRSBaseModel):
    """Response containing average prices enriched with item metadata."""

    items: list[EnrichedAveragePrice]
    timestamp: int


class EnrichedTimeseriesResponse(OSRSBaseModel):
    """Timeseries response with item metadata attached."""

    item: ItemMapping
    data: list[TimeseriesDataPoint]
