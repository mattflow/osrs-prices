from http import HTTPStatus
from typing import Literal
import os
import httpx
import pandas as pd


class Client:
    def __init__(self, user_agent: str, game_mode: Literal["osrs", "dmm"] = "osrs"):
        self.user_agent = user_agent
        self.base_url = os.path.join("https://prices.runescape.wiki/api/v1", game_mode)
        self.headers = {"User-Agent": self.user_agent}

    def _get_request_data(self, endpoint: str):
        with httpx.Client(headers=self.headers, base_url=self.base_url) as client:
            response = client.get(endpoint)

        assert response.status_code == HTTPStatus.OK
        return response.json()

    def get_mapping(self, as_pandas: bool = False):
        data = self._get_request_data("mapping")
        if not as_pandas:
            return data
        df = pd.DataFrame.from_records(data)
        return df

    def get_latest(self, as_pandas: bool = False, mapped: bool = False):
        data = self._get_request_data("latest")["data"]
        if not as_pandas:
            return data

        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.reset_index().rename(columns={"index": "id"})
        df["id"] = df["id"].astype(int)

        if mapped:
            df = df.merge(self.get_mapping(as_pandas=True), on="id", how="inner")

        return df
