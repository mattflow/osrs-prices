from osrs_prices.client import Client, PricePoint
from osrs_prices.client import Item
import pytest


@pytest.fixture
def osrs_client() -> Client:
    return Client(
        user_agent="osrs-prices integration test - https://github.com/mattflow/osrs-prices",
        game_mode="osrs",
    )


@pytest.fixture
def dmm_client() -> Client:
    return Client(
        user_agent="osrs-prices integration test - https://github.com/mattflow/osrs-prices",
        game_mode="dmm",
    )


def test_get_mapping(osrs_client: Client, dmm_client: Client) -> None:
    osrs_mapping = osrs_client.get_mapping()
    dmm_mapping = dmm_client.get_mapping()

    assert len(osrs_mapping) > 0
    assert len(dmm_mapping) > 0

    osrs_item_dict = osrs_mapping[0].model_dump()
    dmm_item_dict = dmm_mapping[0].model_dump()

    assert all(field in osrs_item_dict for field in Item.model_fields)
    assert all(field in dmm_item_dict for field in Item.model_fields)


def test_get_latest(osrs_client: Client, dmm_client: Client) -> None:
    osrs_latest = osrs_client.get_latest()
    dmm_latest = dmm_client.get_latest()

    osrs_latest_keys = osrs_latest.keys()
    dmm_latest_keys = dmm_latest.keys()

    assert len(osrs_latest_keys) > 0
    assert len(dmm_latest_keys) > 0

    osrs_price_point_dict = osrs_latest[next(iter(osrs_latest))].model_dump()
    dmm_price_point_dict = dmm_latest[next(iter(dmm_latest))].model_dump()

    assert all(field in osrs_price_point_dict for field in PricePoint.model_fields)
    assert all(field in dmm_price_point_dict for field in PricePoint.model_fields)
