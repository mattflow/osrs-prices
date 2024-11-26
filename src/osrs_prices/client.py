from functools import lru_cache
from http import HTTPStatus
from typing import Any, Dict, List, Literal, Optional, Union, overload
import os
import httpx
import pandas as pd
from pydantic import BaseModel, ConfigDict, TypeAdapter


class Item(BaseModel):
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


class Client:
    def __init__(self, user_agent: str, game_mode: Literal["osrs", "dmm"] = "osrs"):
        self.user_agent = user_agent
        self.base_url = os.path.join("https://prices.runescape.wiki/api/v1", game_mode)
        self.headers = {"User-Agent": self.user_agent}

    def _get_request_data(self, path: str) -> Any:
        with httpx.Client(headers=self.headers, base_url=self.base_url) as client:
            response = client.get(path)

        assert response.status_code == HTTPStatus.OK
        return response.json()

    @lru_cache(maxsize=1)
    def _get_mapping_data(self) -> Any:
        return self._get_request_data("mapping")

    @overload
    def get_mapping(
        self, as_pandas: Literal[True], force_refresh: bool = False
    ) -> pd.DataFrame: ...
    @overload
    def get_mapping(
        self, as_pandas: Literal[False], force_refresh: bool = False
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
        data = self._get_request_data("latest")
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
        self, as_pandas: bool = False, mapped: bool = False
    ) -> Union[Latest, pd.DataFrame]:
        data = self._get_latest_data()

        if not as_pandas:
            return LatestAdapter.validate_python(data)

        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.reset_index().rename(columns={"index": "id"})
        df["id"] = df["id"].astype(int)

        if mapped:
            df = df.merge(self.get_mapping(as_pandas=True), on="id", how="inner")

        return df
