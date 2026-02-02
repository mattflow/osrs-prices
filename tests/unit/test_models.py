"""Unit tests for Pydantic models."""

import pytest

from osrs_prices.models import (
    AveragePrice,
    AverageResponse,
    ItemMapping,
    LatestPrice,
    LatestResponse,
    MappingResponse,
    TimeseriesDataPoint,
    TimeseriesResponse,
)


class TestItemMapping:
    """Tests for ItemMapping model."""

    def test_create_item_mapping(self) -> None:
        """Test creating an ItemMapping from valid data."""
        item = ItemMapping(
            id=4151,
            name="Abyssal whip",
            examine="A weapon from the abyss.",
            members=True,
            lowalch=28800,
            highalch=43200,
            limit=70,
            value=72000,
            icon="Abyssal_whip.png",
        )
        assert item.id == 4151
        assert item.name == "Abyssal whip"
        assert item.members is True
        assert item.limit == 70

    def test_optional_fields(self) -> None:
        """Test that optional fields default to None."""
        item = ItemMapping(
            id=1,
            name="Test",
            examine="Test item",
            members=False,
            value=100,
            icon="test.png",
        )
        assert item.lowalch is None
        assert item.highalch is None
        assert item.limit is None

    def test_frozen_model(self) -> None:
        """Test that model is frozen (immutable)."""
        item = ItemMapping(
            id=1,
            name="Test",
            examine="Test item",
            members=False,
            value=100,
            icon="test.png",
        )
        with pytest.raises(Exception):  # ValidationError from Pydantic
            item.name = "New name"  # type: ignore[misc]


class TestMappingResponse:
    """Tests for MappingResponse model."""

    def test_from_list(self, sample_mapping_response: list[dict]) -> None:
        """Test creating MappingResponse from API list."""
        response = MappingResponse.from_list(sample_mapping_response)
        assert len(response.items) == 3
        assert response.items[0].name == "Abyssal whip"
        assert response.items[1].name == "Cannonball"

    def test_empty_list(self) -> None:
        """Test creating MappingResponse from empty list."""
        response = MappingResponse.from_list([])
        assert len(response.items) == 0


class TestLatestPrice:
    """Tests for LatestPrice model."""

    def test_create_with_alias(self) -> None:
        """Test creating LatestPrice with camelCase fields."""
        price = LatestPrice.model_validate({
            "high": 1500000,
            "highTime": 1704067200,
            "low": 1480000,
            "lowTime": 1704067180,
        })
        assert price.high == 1500000
        assert price.high_time == 1704067200
        assert price.low == 1480000
        assert price.low_time == 1704067180

    def test_all_optional(self) -> None:
        """Test that all fields can be None."""
        price = LatestPrice()
        assert price.high is None
        assert price.high_time is None
        assert price.low is None
        assert price.low_time is None


class TestLatestResponse:
    """Tests for LatestResponse model."""

    def test_from_api(self, sample_latest_response: dict) -> None:
        """Test creating LatestResponse from API data."""
        response = LatestResponse.from_api(sample_latest_response)
        assert 4151 in response.data
        assert 2 in response.data
        assert response.data[4151].high == 1500000

    def test_empty_data(self) -> None:
        """Test creating LatestResponse with empty data."""
        response = LatestResponse.from_api({"data": {}})
        assert len(response.data) == 0


class TestAveragePrice:
    """Tests for AveragePrice model."""

    def test_create_with_alias(self) -> None:
        """Test creating AveragePrice with camelCase fields."""
        price = AveragePrice.model_validate({
            "avgHighPrice": 1495000,
            "highPriceVolume": 50,
            "avgLowPrice": 1485000,
            "lowPriceVolume": 45,
        })
        assert price.avg_high_price == 1495000
        assert price.high_price_volume == 50
        assert price.avg_low_price == 1485000
        assert price.low_price_volume == 45


class TestAverageResponse:
    """Tests for AverageResponse model."""

    def test_from_api(self, sample_5m_response: dict) -> None:
        """Test creating AverageResponse from API data."""
        response = AverageResponse.from_api(sample_5m_response)
        assert response.timestamp == 1704067200
        assert 4151 in response.data
        assert response.data[4151].avg_high_price == 1495000


class TestTimeseriesDataPoint:
    """Tests for TimeseriesDataPoint model."""

    def test_create_with_alias(self) -> None:
        """Test creating TimeseriesDataPoint with camelCase fields."""
        point = TimeseriesDataPoint.model_validate({
            "timestamp": 1704067200,
            "avgHighPrice": 1500000,
            "avgLowPrice": 1480000,
            "highPriceVolume": 100,
            "lowPriceVolume": 95,
        })
        assert point.timestamp == 1704067200
        assert point.avg_high_price == 1500000


class TestTimeseriesResponse:
    """Tests for TimeseriesResponse model."""

    def test_from_api(self, sample_timeseries_response: dict) -> None:
        """Test creating TimeseriesResponse from API data."""
        response = TimeseriesResponse.from_api(sample_timeseries_response)
        assert len(response.data) == 3
        assert response.data[0].timestamp == 1704067200
        assert response.data[0].avg_high_price == 1500000

    def test_empty_data(self) -> None:
        """Test creating TimeseriesResponse with empty data."""
        response = TimeseriesResponse.from_api({"data": []})
        assert len(response.data) == 0
