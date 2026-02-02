"""Integration tests that hit the real OSRS Prices API.

These tests are marked with @pytest.mark.integration and are skipped by default.
Run with: uv run pytest -m integration
"""

import pytest

from osrs_prices import Client


@pytest.fixture
def client() -> Client:
    """Create a real client for integration testing."""
    return Client(user_agent="osrs-prices-integration-tests/1.0")


@pytest.mark.integration
class TestRealAPI:
    """Integration tests against the real API."""

    def test_get_mapping(self, client: Client) -> None:
        """Test fetching item mapping from real API."""
        with client:
            mapping = client.get_mapping()

            # Should have many items
            assert len(mapping.items) > 1000

            # Check for known item - Abyssal whip (4151)
            whip = next((item for item in mapping.items if item.id == 4151), None)
            assert whip is not None
            assert whip.name == "Abyssal whip"
            assert whip.members is True

    def test_get_latest(self, client: Client) -> None:
        """Test fetching latest prices from real API."""
        with client:
            latest = client.get_latest()

            # Should have price data
            assert len(latest.data) > 0

            # Check for Abyssal whip price
            if 4151 in latest.data:
                whip_price = latest.data[4151]
                # Price should be reasonable (not 0 or negative)
                if whip_price.high is not None:
                    assert whip_price.high > 0
                if whip_price.low is not None:
                    assert whip_price.low > 0

    def test_get_latest_single_item(self, client: Client) -> None:
        """Test fetching single item price from real API."""
        with client:
            latest = client.get_latest(item_id=4151)

            # Should only have the requested item
            assert 4151 in latest.data

    def test_get_5m_average(self, client: Client) -> None:
        """Test fetching 5-minute averages from real API."""
        with client:
            averages = client.get_5m_average()

            assert averages.timestamp > 0
            assert len(averages.data) > 0

    def test_get_1h_average(self, client: Client) -> None:
        """Test fetching 1-hour averages from real API."""
        with client:
            averages = client.get_1h_average()

            assert averages.timestamp > 0
            assert len(averages.data) > 0

    def test_get_timeseries(self, client: Client) -> None:
        """Test fetching timeseries data from real API."""
        with client:
            # Get timeseries for Abyssal whip
            timeseries = client.get_timeseries(item_id=4151, timestep="1h")

            # Should have historical data points
            assert len(timeseries.data) > 0

            # Each point should have a timestamp
            for point in timeseries.data:
                assert point.timestamp > 0

    def test_get_item_by_name(self, client: Client) -> None:
        """Test finding an item by name."""
        with client:
            whip = client.get_item_by_name("Abyssal whip")

            assert whip is not None
            assert whip.id == 4151

    def test_mapping_caching(self, client: Client) -> None:
        """Test that mapping data is cached."""
        with client:
            # First call
            mapping1 = client.get_mapping()

            # Second call should return same object (from cache)
            mapping2 = client.get_mapping()

            assert mapping1 is mapping2
