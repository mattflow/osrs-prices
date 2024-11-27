from functools import lru_cache
from http import HTTPStatus
from typing import Any, Dict, List, Literal, Optional, Union, overload
import os
import httpx
import pandas as pd
from pydantic import BaseModel, ConfigDict, TypeAdapter


class Item(BaseModel):
    name: str
    icon: str
    highalch: Optional[int] = None
    lowalch: Optional[int] = None
    limit: Optional[int] = None
    value: int
    examine: str
    members: bool
    id: int
    model_config = ConfigDict(extra="forbid")


Mapping = List[Item]
MappingAdapter = TypeAdapter(Mapping)


class PricePoint(BaseModel):
    lowTime: Optional[int] = None
    low: Optional[int] = None
    highTime: Optional[int] = None
    high: Optional[int] = None
    model_config = ConfigDict(extra="forbid")


Latest = Dict[str, PricePoint]
LatestAdapter = TypeAdapter(Latest)


def get_request_data(*, headers: dict[str, str], base_url: str, endpoint: str) -> Any:
    with httpx.Client(headers=headers, base_url=base_url) as client:
        response = client.get(endpoint)

    assert response.status_code == HTTPStatus.OK
    return response.json()


class Client:
    def __init__(self, user_agent: str, game_mode: Literal["osrs", "dmm"] = "osrs"):
        self.base_url = os.path.join("https://prices.runescape.wiki/api/v1", game_mode)
        self.headers = {"User-Agent": user_agent}

    @lru_cache(maxsize=1)
    def _get_mapping_data(self) -> Any:
        return get_request_data(
            headers=self.headers, base_url=self.base_url, endpoint="mapping"
        )

    @overload
    def get_mapping(
        self, as_pandas: Literal[True], force_refresh: bool = False
    ) -> pd.DataFrame: ...
    @overload
    def get_mapping(
        self, as_pandas: Literal[False] = False, force_refresh: bool = False
    ) -> Mapping: ...
    def get_mapping(
        self, as_pandas: bool = False, force_refresh: bool = False
    ) -> Union[Mapping, pd.DataFrame]:
        if force_refresh:
            self._get_mapping_data.cache_clear()

        data = self._get_mapping_data()

        if not as_pandas:
            return MappingAdapter.validate_python(data)

        df = pd.DataFrame.from_records(data)
        df["id"] = df["id"].astype(int)

        return df

    def _get_latest_data(self) -> Any:
        data = get_request_data(
            headers=self.headers, base_url=self.base_url, endpoint="latest"
        )
        assert "data" in data
        return data["data"]

    @overload
    def get_latest(
        self, as_pandas: Literal[True], mapped: bool = False
    ) -> pd.DataFrame: ...
    @overload
    def get_latest(
        self, as_pandas: Literal[False] = False, mapped: bool = False
    ) -> Latest: ...
    def get_latest(
        self, as_pandas: bool = False, mapped: bool = False, force_refresh: bool = False
    ) -> Union[Latest, pd.DataFrame]:
        data = self._get_latest_data()

        if not as_pandas:
            return LatestAdapter.validate_python(data)

        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.reset_index().rename(columns={"index": "id"})
        df["id"] = df["id"].astype(int)

        if mapped:
            df = df.merge(
                self.get_mapping(as_pandas=True, force_refresh=force_refresh),
                on="id",
                how="inner",
            )

        return df
