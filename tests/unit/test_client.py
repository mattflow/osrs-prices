from osrs_prices.client import get_request_data
from osrs_prices import Client
from pytest_mock import MockerFixture
import pytest


def test_get_request_data(mocker: MockerFixture) -> None:
    MockClient = mocker.patch("osrs_prices.client.httpx.Client")
    mock_client = MockClient.return_value.__enter__.return_value
    mock_response = mock_client.get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}

    data = get_request_data(
        headers={"User-Agent": "test user agent"},
        base_url="https://test-base-url.com",
        endpoint="test-endpoint",
    )

    MockClient.assert_called_once_with(
        headers={"User-Agent": "test user agent"}, base_url="https://test-base-url.com"
    )
    mock_client.get.assert_called_once_with("test-endpoint")
    mock_response.json.assert_called_once()
    assert data == {"test": "data"}


def test_get_request_data_status_code_not_200(mocker: MockerFixture) -> None:
    MockClient = mocker.patch("osrs_prices.client.httpx.Client")
    mock_client = MockClient.return_value.__enter__.return_value
    mock_response = mock_client.get.return_value
    mock_response.status_code = 404

    with pytest.raises(AssertionError):
        get_request_data(
            headers={"User-Agent": "test user agent"},
            base_url="https://test-base-url.com",
            endpoint="test-endpoint",
        )

    MockClient.assert_called_once_with(
        headers={"User-Agent": "test user agent"}, base_url="https://test-base-url.com"
    )
    mock_client.get.assert_called_once_with("test-endpoint")


def test_client__get_mapping_data(mocker: MockerFixture) -> None:
    mock_get_request_data = mocker.patch("osrs_prices.client.get_request_data")
    mock_get_request_data.return_value = {"test": "data"}

    client = Client(user_agent="test user agent", game_mode="osrs")
    assert client._get_mapping_data() == {"test": "data"}
    mock_get_request_data.assert_called_once_with(
        headers={"User-Agent": "test user agent"},
        base_url="https://prices.runescape.wiki/api/v1/osrs",
        endpoint="mapping",
    )


def test_client__get_latest_data(mocker: MockerFixture) -> None:
    mock_get_request_data = mocker.patch("osrs_prices.client.get_request_data")
    mock_get_request_data.return_value = {"data": {"test": "data"}}

    client = Client(user_agent="test user agent", game_mode="osrs")
    assert client._get_latest_data() == {"test": "data"}
    mock_get_request_data.assert_called_once_with(
        headers={"User-Agent": "test user agent"},
        base_url="https://prices.runescape.wiki/api/v1/osrs",
        endpoint="latest",
    )
