"""Unit tests for DataFrame conversion utilities."""

import pytest

from osrs_prices.pandas import to_dataframe
from osrs_prices.models import (
    AveragePrice,
    AverageResponse,
    LatestPrice,
    LatestResponse,
    MappingResponse,
    TimeseriesDataPoint,
    TimeseriesResponse,
)
from osrs_prices.models.items import ItemMapping


class TestToDataFrame:
    """Tests for to_dataframe function."""

    def test_mapping_response(self) -> None:
        """Test converting MappingResponse to DataFrame."""
        response = MappingResponse(
            items=[
                ItemMapping(
                    id=4151,
                    name="Abyssal whip",
                    examine="A weapon from the abyss.",
                    members=True,
                    value=72000,
                    icon="Abyssal_whip.png",
                ),
                ItemMapping(
                    id=2,
                    name="Cannonball",
                    examine="Ammo for the Dwarf Cannon.",
                    members=True,
                    value=5,
                    icon="Cannonball.png",
                ),
            ]
        )

        df = to_dataframe(response)

        assert len(df) == 2
        assert df.index.name == "id"
        assert 4151 in df.index
        assert 2 in df.index
        assert df.loc[4151, "name"] == "Abyssal whip"

    def test_latest_response(self) -> None:
        """Test converting LatestResponse to DataFrame."""
        response = LatestResponse(
            data={
                4151: LatestPrice(high=1500000, low=1480000),
                2: LatestPrice(high=150, low=145),
            }
        )

        df = to_dataframe(response)

        assert len(df) == 2
        assert df.index.name == "item_id"
        assert 4151 in df.index
        assert df.loc[4151, "high"] == 1500000
        assert df.loc[4151, "low"] == 1480000

    def test_average_response(self) -> None:
        """Test converting AverageResponse to DataFrame."""
        response = AverageResponse(
            data={
                4151: AveragePrice(
                    avg_high_price=1495000,
                    high_price_volume=50,
                    avg_low_price=1485000,
                    low_price_volume=45,
                ),
            },
            timestamp=1704067200,
        )

        df = to_dataframe(response)

        assert len(df) == 1
        assert df.index.name == "item_id"
        assert df.loc[4151, "avg_high_price"] == 1495000
        assert df.attrs["timestamp"] == 1704067200

    def test_timeseries_response(self) -> None:
        """Test converting TimeseriesResponse to DataFrame."""
        response = TimeseriesResponse(
            data=[
                TimeseriesDataPoint(
                    timestamp=1704067200,
                    avg_high_price=1500000,
                    avg_low_price=1480000,
                ),
                TimeseriesDataPoint(
                    timestamp=1704063600,
                    avg_high_price=1490000,
                    avg_low_price=1470000,
                ),
            ]
        )

        df = to_dataframe(response)

        assert len(df) == 2
        assert df.index.name == "timestamp"
        # Index should be datetime with UTC timezone
        assert "datetime64" in str(df.index.dtype)
        assert "UTC" in str(df.index.dtype)

    def test_empty_responses(self) -> None:
        """Test converting empty responses."""
        mapping_df = to_dataframe(MappingResponse(items=[]))
        assert len(mapping_df) == 0

        latest_df = to_dataframe(LatestResponse(data={}))
        assert len(latest_df) == 0

        average_df = to_dataframe(AverageResponse(data={}, timestamp=0))
        assert len(average_df) == 0

        timeseries_df = to_dataframe(TimeseriesResponse(data=[]))
        assert len(timeseries_df) == 0

    def test_unsupported_type(self) -> None:
        """Test that unsupported types raise TypeError."""
        with pytest.raises(TypeError, match="Unsupported response type"):
            to_dataframe("not a response")  # type: ignore[arg-type]
