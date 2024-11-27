from osrs_prices.client import Client
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
