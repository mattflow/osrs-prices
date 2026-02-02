"""Pytest fixtures and sample API responses."""

import pytest

# Sample API responses for testing


@pytest.fixture
def sample_mapping_response() -> list[dict]:
    """Sample response from /mapping endpoint."""
    return [
        {
            "id": 4151,
            "name": "Abyssal whip",
            "examine": "A weapon from the abyss.",
            "members": True,
            "lowalch": 28800,
            "highalch": 43200,
            "limit": 70,
            "value": 72000,
            "icon": "Abyssal_whip.png",
        },
        {
            "id": 2,
            "name": "Cannonball",
            "examine": "Ammo for the Dwarf Cannon.",
            "members": True,
            "lowalch": 2,
            "highalch": 3,
            "limit": 11000,
            "value": 5,
            "icon": "Cannonball.png",
        },
        {
            "id": 11802,
            "name": "Armadyl godsword",
            "examine": "A very powerful sword.",
            "members": True,
            "lowalch": None,
            "highalch": None,
            "limit": 8,
            "value": 1500000,
            "icon": "Armadyl_godsword.png",
        },
    ]


@pytest.fixture
def sample_latest_response() -> dict:
    """Sample response from /latest endpoint."""
    return {
        "data": {
            "4151": {
                "high": 1500000,
                "highTime": 1704067200,
                "low": 1480000,
                "lowTime": 1704067180,
            },
            "2": {
                "high": 150,
                "highTime": 1704067190,
                "low": 145,
                "lowTime": 1704067150,
            },
        }
    }


@pytest.fixture
def sample_latest_single_item_response() -> dict:
    """Sample response from /latest?id=4151 endpoint."""
    return {
        "data": {
            "4151": {
                "high": 1500000,
                "highTime": 1704067200,
                "low": 1480000,
                "lowTime": 1704067180,
            }
        }
    }


@pytest.fixture
def sample_5m_response() -> dict:
    """Sample response from /5m endpoint."""
    return {
        "data": {
            "4151": {
                "avgHighPrice": 1495000,
                "highPriceVolume": 50,
                "avgLowPrice": 1485000,
                "lowPriceVolume": 45,
            },
            "2": {
                "avgHighPrice": 148,
                "highPriceVolume": 10000,
                "avgLowPrice": 146,
                "lowPriceVolume": 9500,
            },
        },
        "timestamp": 1704067200,
    }


@pytest.fixture
def sample_1h_response() -> dict:
    """Sample response from /1h endpoint."""
    return {
        "data": {
            "4151": {
                "avgHighPrice": 1498000,
                "highPriceVolume": 500,
                "avgLowPrice": 1488000,
                "lowPriceVolume": 480,
            },
        },
        "timestamp": 1704067200,
    }


@pytest.fixture
def sample_timeseries_response() -> dict:
    """Sample response from /timeseries endpoint."""
    return {
        "data": [
            {
                "timestamp": 1704067200,
                "avgHighPrice": 1500000,
                "avgLowPrice": 1480000,
                "highPriceVolume": 100,
                "lowPriceVolume": 95,
            },
            {
                "timestamp": 1704063600,
                "avgHighPrice": 1490000,
                "avgLowPrice": 1470000,
                "highPriceVolume": 120,
                "lowPriceVolume": 110,
            },
            {
                "timestamp": 1704060000,
                "avgHighPrice": 1485000,
                "avgLowPrice": 1465000,
                "highPriceVolume": 80,
                "lowPriceVolume": 75,
            },
        ]
    }
