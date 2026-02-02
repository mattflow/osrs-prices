"""Unit tests for enriched models and client methods."""

from unittest.mock import MagicMock, patch

import pytest

from osrs_prices import (
    Client,
    EnrichedAveragePrice,
    EnrichedAverageResponse,
    EnrichedLatestPrice,
    EnrichedLatestResponse,
    EnrichedTimeseriesResponse,
    TimeseriesResponse,
    ValidationError,
)
from osrs_prices.models.timeseries import TimeseriesDataPoint


class TestEnrichedModels:
    """Tests for enriched model construction."""

    def test_enriched_latest_price_construction(self) -> None:
        """Test EnrichedLatestPrice can be constructed with all fields."""
        price = EnrichedLatestPrice(
            id=4151,
            name="Abyssal whip",
            examine="A weapon from the abyss.",
            members=True,
            lowalch=28800,
            highalch=43200,
            limit=70,
            value=72000,
            icon="Abyssal_whip.png",
            high=1500000,
            high_time=1704067200,
            low=1480000,
            low_time=1704067180,
        )

        assert price.id == 4151
        assert price.name == "Abyssal whip"
        assert price.high == 1500000
        assert price.limit == 70

    def test_enriched_latest_price_optional_fields(self) -> None:
        """Test EnrichedLatestPrice with optional fields as None."""
        price = EnrichedLatestPrice(
            id=4151,
            name="Abyssal whip",
            members=True,
            icon="Abyssal_whip.png",
        )

        assert price.examine is None
        assert price.high is None
        assert price.low is None

    def test_enriched_latest_response(self) -> None:
        """Test EnrichedLatestResponse construction."""
        items = [
            EnrichedLatestPrice(
                id=4151,
                name="Abyssal whip",
                members=True,
                icon="Abyssal_whip.png",
                high=1500000,
            ),
            EnrichedLatestPrice(
                id=2,
                name="Cannonball",
                members=True,
                icon="Cannonball.png",
                high=150,
            ),
        ]
        response = EnrichedLatestResponse(items=items)

        assert len(response.items) == 2
        assert response.items[0].name == "Abyssal whip"

    def test_enriched_average_price_construction(self) -> None:
        """Test EnrichedAveragePrice can be constructed with all fields."""
        price = EnrichedAveragePrice(
            id=4151,
            name="Abyssal whip",
            members=True,
            icon="Abyssal_whip.png",
            avg_high_price=1495000,
            high_price_volume=50,
            avg_low_price=1485000,
            low_price_volume=45,
        )

        assert price.id == 4151
        assert price.avg_high_price == 1495000
        assert price.high_price_volume == 50

    def test_enriched_average_response(self) -> None:
        """Test EnrichedAverageResponse construction."""
        items = [
            EnrichedAveragePrice(
                id=4151,
                name="Abyssal whip",
                members=True,
                icon="Abyssal_whip.png",
            ),
        ]
        response = EnrichedAverageResponse(items=items, timestamp=1704067200)

        assert len(response.items) == 1
        assert response.timestamp == 1704067200


class TestClientEnrichedMethods:
    """Tests for client enriched methods with mocked HTTP."""

    @pytest.fixture
    def mock_client(self) -> Client:
        """Create a client with mocked HTTP."""
        return Client(user_agent="test/1.0")

    def test_get_latest_with_mapping(
        self,
        mock_client: Client,
        sample_latest_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_latest_with_mapping method."""
        mock_latest_resp = MagicMock()
        mock_latest_resp.status_code = 200
        mock_latest_resp.json.return_value = sample_latest_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_latest_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            result = mock_client.get_latest_with_mapping()

            assert isinstance(result, EnrichedLatestResponse)
            assert len(result.items) == 2

            whip = next((item for item in result.items if item.id == 4151), None)
            assert whip is not None
            assert whip.name == "Abyssal whip"
            assert whip.high == 1500000
            assert whip.limit == 70

        mock_client.close()

    def test_get_latest_with_mapping_single_item(
        self,
        mock_client: Client,
        sample_latest_single_item_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_latest_with_mapping with specific item_id."""
        mock_latest_resp = MagicMock()
        mock_latest_resp.status_code = 200
        mock_latest_resp.json.return_value = sample_latest_single_item_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_latest_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            result = mock_client.get_latest_with_mapping(item_id=4151)

            assert len(result.items) == 1
            assert result.items[0].id == 4151
            assert result.items[0].name == "Abyssal whip"

        mock_client.close()

    def test_get_5m_average_with_mapping(
        self,
        mock_client: Client,
        sample_5m_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_5m_average_with_mapping method."""
        mock_avg_resp = MagicMock()
        mock_avg_resp.status_code = 200
        mock_avg_resp.json.return_value = sample_5m_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_avg_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            result = mock_client.get_5m_average_with_mapping()

            assert isinstance(result, EnrichedAverageResponse)
            assert result.timestamp == 1704067200
            assert len(result.items) == 2

            whip = next((item for item in result.items if item.id == 4151), None)
            assert whip is not None
            assert whip.name == "Abyssal whip"
            assert whip.avg_high_price == 1495000

        mock_client.close()

    def test_get_1h_average_with_mapping(
        self,
        mock_client: Client,
        sample_1h_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_1h_average_with_mapping method."""
        mock_avg_resp = MagicMock()
        mock_avg_resp.status_code = 200
        mock_avg_resp.json.return_value = sample_1h_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_avg_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            result = mock_client.get_1h_average_with_mapping()

            assert isinstance(result, EnrichedAverageResponse)
            assert result.timestamp == 1704067200
            assert len(result.items) == 1

        mock_client.close()

    def test_get_timeseries_with_mapping(
        self,
        mock_client: Client,
        sample_timeseries_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_timeseries_with_mapping method."""
        mock_ts_resp = MagicMock()
        mock_ts_resp.status_code = 200
        mock_ts_resp.json.return_value = sample_timeseries_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_ts_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            result = mock_client.get_timeseries_with_mapping(item_id=4151, timestep="1h")

            assert isinstance(result, EnrichedTimeseriesResponse)
            assert result.item.id == 4151
            assert result.item.name == "Abyssal whip"
            assert len(result.data) == 3

        mock_client.close()

    def test_get_timeseries_with_mapping_unknown_item(
        self,
        mock_client: Client,
        sample_timeseries_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test get_timeseries_with_mapping raises for unknown item."""
        mock_ts_resp = MagicMock()
        mock_ts_resp.status_code = 200
        mock_ts_resp.json.return_value = sample_timeseries_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_ts_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            with pytest.raises(ValidationError, match="not found in mapping"):
                mock_client.get_timeseries_with_mapping(item_id=99999, timestep="1h")

        mock_client.close()

    def test_enrich_latest_response(
        self,
        mock_client: Client,
        sample_latest_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test enrich method with LatestResponse."""
        mock_latest_resp = MagicMock()
        mock_latest_resp.status_code = 200
        mock_latest_resp.json.return_value = sample_latest_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_latest_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            latest = mock_client.get_latest()
            enriched = mock_client.enrich(latest)

            assert isinstance(enriched, EnrichedLatestResponse)
            assert len(enriched.items) == 2

        mock_client.close()

    def test_enrich_average_response(
        self,
        mock_client: Client,
        sample_5m_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test enrich method with AverageResponse."""
        mock_avg_resp = MagicMock()
        mock_avg_resp.status_code = 200
        mock_avg_resp.json.return_value = sample_5m_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_avg_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            averages = mock_client.get_5m_average()
            enriched = mock_client.enrich(averages)

            assert isinstance(enriched, EnrichedAverageResponse)
            assert enriched.timestamp == 1704067200
            assert len(enriched.items) == 2

        mock_client.close()

    def test_enriched_methods_use_cached_mapping(
        self,
        mock_client: Client,
        sample_latest_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test that enriched methods use cached mapping data."""
        mock_latest_resp = MagicMock()
        mock_latest_resp.status_code = 200
        mock_latest_resp.json.return_value = sample_latest_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        mapping_calls = []

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                mapping_calls.append(url)
                return mock_mapping_resp
            return mock_latest_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            # First call should hit mapping API
            mock_client.get_latest_with_mapping()
            assert len(mapping_calls) == 1

            # Second call should use cache
            mock_client.get_latest_with_mapping()
            assert len(mapping_calls) == 1

        mock_client.close()

    def test_enrich_timeseries_response(
        self,
        mock_client: Client,
        sample_timeseries_response: dict,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test enrich method with TimeseriesResponse."""
        mock_ts_resp = MagicMock()
        mock_ts_resp.status_code = 200
        mock_ts_resp.json.return_value = sample_timeseries_response

        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        def mock_get(url: str, **kwargs) -> MagicMock:
            if "/mapping" in url:
                return mock_mapping_resp
            return mock_ts_resp

        with patch.object(mock_client._http_client, "get", side_effect=mock_get):
            timeseries = mock_client.get_timeseries(item_id=4151, timestep="1h")
            enriched = mock_client.enrich(timeseries)

            assert isinstance(enriched, EnrichedTimeseriesResponse)
            assert enriched.item.id == 4151
            assert enriched.item.name == "Abyssal whip"
            assert len(enriched.data) == 3

        mock_client.close()

    def test_enrich_timeseries_without_item_id(
        self,
        mock_client: Client,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test enrich raises for TimeseriesResponse without item_id."""
        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        # Create a TimeseriesResponse without item_id
        timeseries = TimeseriesResponse(
            data=[
                TimeseriesDataPoint(
                    timestamp=1704067200,
                    avg_high_price=1500000,
                    avg_low_price=1480000,
                )
            ]
        )

        with patch.object(mock_client._http_client, "get", return_value=mock_mapping_resp):
            with pytest.raises(ValidationError, match="without item_id"):
                mock_client.enrich(timeseries)

        mock_client.close()

    def test_enrich_timeseries_unknown_item(
        self,
        mock_client: Client,
        sample_mapping_response: list[dict],
    ) -> None:
        """Test enrich raises for TimeseriesResponse with unknown item_id."""
        mock_mapping_resp = MagicMock()
        mock_mapping_resp.status_code = 200
        mock_mapping_resp.json.return_value = sample_mapping_response

        # Create a TimeseriesResponse with unknown item_id
        timeseries = TimeseriesResponse(
            item_id=99999,
            data=[
                TimeseriesDataPoint(
                    timestamp=1704067200,
                    avg_high_price=1500000,
                    avg_low_price=1480000,
                )
            ]
        )

        with patch.object(mock_client._http_client, "get", return_value=mock_mapping_resp):
            with pytest.raises(ValidationError, match="not found in mapping"):
                mock_client.enrich(timeseries)

        mock_client.close()
