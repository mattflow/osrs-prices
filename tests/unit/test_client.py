"""Unit tests for the Client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from osrs_prices import Client, ValidationError
from osrs_prices.models import LatestResponse, MappingResponse


class TestClientValidation:
    """Tests for client initialization and validation."""

    def test_empty_user_agent_raises(self) -> None:
        """Test that empty user agent raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            Client(user_agent="")

    def test_whitespace_user_agent_raises(self) -> None:
        """Test that whitespace-only user agent raises ValidationError."""
        with pytest.raises(ValidationError, match="must not be empty"):
            Client(user_agent="   ")

    def test_blocked_user_agent_python_requests(self) -> None:
        """Test that python-requests user agent is blocked."""
        with pytest.raises(ValidationError, match="blocked agent"):
            Client(user_agent="python-requests/2.31.0")

    def test_blocked_user_agent_httpx(self) -> None:
        """Test that python-httpx user agent is blocked."""
        with pytest.raises(ValidationError, match="blocked agent"):
            Client(user_agent="python-httpx/0.27.0")

    def test_valid_user_agent(self) -> None:
        """Test that valid user agent is accepted."""
        client = Client(user_agent="my-app/1.0 contact@example.com")
        client.close()


class TestClientContextManager:
    """Tests for context manager functionality."""

    def test_context_manager(self) -> None:
        """Test that client works as context manager."""
        with Client(user_agent="test/1.0") as client:
            assert client is not None

    def test_close_called_on_exit(self) -> None:
        """Test that close is called when exiting context."""
        with patch.object(httpx.Client, "close") as mock_close:
            with Client(user_agent="test/1.0"):
                pass
            mock_close.assert_called_once()


class TestClientMethods:
    """Tests for client API methods with mocked HTTP."""

    @pytest.fixture
    def mock_client(self) -> Client:
        """Create a client with mocked HTTP."""
        return Client(user_agent="test/1.0")

    def test_get_latest(
        self, mock_client: Client, sample_latest_response: dict
    ) -> None:
        """Test get_latest method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_latest_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            result = mock_client.get_latest()

            mock_get.assert_called_once()
            assert isinstance(result, LatestResponse)
            assert 4151 in result.data
            assert result.data[4151].high == 1500000

        mock_client.close()

    def test_get_latest_with_item_id(
        self, mock_client: Client, sample_latest_single_item_response: dict
    ) -> None:
        """Test get_latest with specific item_id."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_latest_single_item_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            result = mock_client.get_latest(item_id=4151)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"] == {"id": "4151"}
            assert 4151 in result.data

        mock_client.close()

    def test_get_mapping(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test get_mapping method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ):
            result = mock_client.get_mapping()

            assert isinstance(result, MappingResponse)
            assert len(result.items) == 3
            assert result.items[0].name == "Abyssal whip"

        mock_client.close()

    def test_get_mapping_caching(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test that get_mapping uses cache."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            # First call should hit API
            result1 = mock_client.get_mapping()
            assert mock_get.call_count == 1

            # Second call should use cache
            result2 = mock_client.get_mapping()
            assert mock_get.call_count == 1  # No additional call

            # Results should be identical
            assert result1 == result2

        mock_client.close()

    def test_get_mapping_force_refresh(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test that force_refresh bypasses cache."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            mock_client.get_mapping()
            assert mock_get.call_count == 1

            mock_client.get_mapping(force_refresh=True)
            assert mock_get.call_count == 2

        mock_client.close()

    def test_get_5m_average(
        self, mock_client: Client, sample_5m_response: dict
    ) -> None:
        """Test get_5m_average method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_5m_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ):
            result = mock_client.get_5m_average()

            assert result.timestamp == 1704067200
            assert 4151 in result.data

        mock_client.close()

    def test_get_1h_average(
        self, mock_client: Client, sample_1h_response: dict
    ) -> None:
        """Test get_1h_average method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_1h_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ):
            result = mock_client.get_1h_average()

            assert result.timestamp == 1704067200
            assert 4151 in result.data

        mock_client.close()

    def test_get_timeseries(
        self, mock_client: Client, sample_timeseries_response: dict
    ) -> None:
        """Test get_timeseries method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_timeseries_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            result = mock_client.get_timeseries(item_id=4151, timestep="1h")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"] == {"id": "4151", "timestep": "1h"}
            assert len(result.data) == 3

        mock_client.close()

    def test_get_item_by_name(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test get_item_by_name convenience method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ):
            result = mock_client.get_item_by_name("Abyssal whip")

            assert result is not None
            assert result.id == 4151
            assert result.name == "Abyssal whip"

        mock_client.close()

    def test_get_item_by_name_not_found(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test get_item_by_name returns None for unknown item."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ):
            result = mock_client.get_item_by_name("Nonexistent item")

            assert result is None

        mock_client.close()

    def test_invalidate_mapping_cache(
        self, mock_client: Client, sample_mapping_response: list[dict]
    ) -> None:
        """Test invalidate_mapping_cache method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_mapping_response

        with patch.object(
            mock_client._http_client, "get", return_value=mock_response
        ) as mock_get:
            mock_client.get_mapping()
            assert mock_get.call_count == 1

            mock_client.invalidate_mapping_cache()

            mock_client.get_mapping()
            assert mock_get.call_count == 2

        mock_client.close()
