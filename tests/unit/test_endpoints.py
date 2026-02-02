"""Unit tests for endpoint classes."""

from unittest.mock import MagicMock

import httpx
import pytest

from osrs_prices.endpoints import (
    FiveMinuteEndpoint,
    LatestEndpoint,
    MappingEndpoint,
    OneHourEndpoint,
    TimeseriesEndpoint,
)
from osrs_prices.exceptions import APIError, RateLimitError


class TestBaseEndpointErrors:
    """Tests for error handling in base endpoint."""

    def test_rate_limit_error(self) -> None:
        """Test that 429 status raises RateLimitError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_client.get.return_value = mock_response

        endpoint = LatestEndpoint(mock_client)

        with pytest.raises(RateLimitError):
            endpoint.fetch()

    def test_api_error(self) -> None:
        """Test that non-200 status raises APIError."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.get.return_value = mock_response

        endpoint = LatestEndpoint(mock_client)

        with pytest.raises(APIError) as exc_info:
            endpoint.fetch()

        assert exc_info.value.status_code == 500


class TestLatestEndpoint:
    """Tests for LatestEndpoint."""

    def test_path(self) -> None:
        """Test that path is correct."""
        mock_client = MagicMock(spec=httpx.Client)
        endpoint = LatestEndpoint(mock_client)
        assert endpoint.path == "/latest"

    def test_fetch_no_params(self, sample_latest_response: dict) -> None:
        """Test fetch without parameters."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_latest_response
        mock_client.get.return_value = mock_response

        endpoint = LatestEndpoint(mock_client)
        result = endpoint.fetch()

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1].get("params") is None
        assert 4151 in result.data

    def test_fetch_with_item_id(self, sample_latest_response: dict) -> None:
        """Test fetch with item_id parameter."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_latest_response
        mock_client.get.return_value = mock_response

        endpoint = LatestEndpoint(mock_client)
        endpoint.fetch(item_id=4151)

        call_args = mock_client.get.call_args
        assert call_args[1]["params"] == {"id": "4151"}


class TestMappingEndpoint:
    """Tests for MappingEndpoint."""

    def test_path(self) -> None:
        """Test that path is correct."""
        mock_client = MagicMock(spec=httpx.Client)
        endpoint = MappingEndpoint(mock_client)
        assert endpoint.path == "/mapping"

    def test_caching(self, sample_mapping_response: list[dict]) -> None:
        """Test that responses are cached."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response
        mock_client.get.return_value = mock_response

        endpoint = MappingEndpoint(mock_client, cache_ttl=3600)

        # First fetch should call API
        endpoint.fetch()
        assert mock_client.get.call_count == 1

        # Second fetch should use cache
        endpoint.fetch()
        assert mock_client.get.call_count == 1

    def test_force_refresh(self, sample_mapping_response: list[dict]) -> None:
        """Test force_refresh bypasses cache."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response
        mock_client.get.return_value = mock_response

        endpoint = MappingEndpoint(mock_client, cache_ttl=3600)

        endpoint.fetch()
        endpoint.fetch(force_refresh=True)

        assert mock_client.get.call_count == 2

    def test_invalidate_cache(self, sample_mapping_response: list[dict]) -> None:
        """Test cache invalidation."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response
        mock_client.get.return_value = mock_response

        endpoint = MappingEndpoint(mock_client, cache_ttl=3600)

        endpoint.fetch()
        endpoint.invalidate_cache()
        endpoint.fetch()

        assert mock_client.get.call_count == 2


class TestFiveMinuteEndpoint:
    """Tests for FiveMinuteEndpoint."""

    def test_path(self) -> None:
        """Test that path is correct."""
        mock_client = MagicMock(spec=httpx.Client)
        endpoint = FiveMinuteEndpoint(mock_client)
        assert endpoint.path == "/5m"

    def test_fetch_with_timestamp(self, sample_5m_response: dict) -> None:
        """Test fetch with timestamp parameter."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_5m_response
        mock_client.get.return_value = mock_response

        endpoint = FiveMinuteEndpoint(mock_client)
        endpoint.fetch(timestamp=1704067200)

        call_args = mock_client.get.call_args
        assert call_args[1]["params"] == {"timestamp": "1704067200"}


class TestOneHourEndpoint:
    """Tests for OneHourEndpoint."""

    def test_path(self) -> None:
        """Test that path is correct."""
        mock_client = MagicMock(spec=httpx.Client)
        endpoint = OneHourEndpoint(mock_client)
        assert endpoint.path == "/1h"


class TestTimeseriesEndpoint:
    """Tests for TimeseriesEndpoint."""

    def test_path(self) -> None:
        """Test that path is correct."""
        mock_client = MagicMock(spec=httpx.Client)
        endpoint = TimeseriesEndpoint(mock_client)
        assert endpoint.path == "/timeseries"

    def test_fetch_with_required_params(
        self, sample_timeseries_response: dict
    ) -> None:
        """Test fetch with required parameters."""
        mock_client = MagicMock(spec=httpx.Client)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_timeseries_response
        mock_client.get.return_value = mock_response

        endpoint = TimeseriesEndpoint(mock_client)
        result = endpoint.fetch(item_id=4151, timestep="1h")

        call_args = mock_client.get.call_args
        assert call_args[1]["params"] == {"id": "4151", "timestep": "1h"}
        assert len(result.data) == 3
