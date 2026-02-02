"""Pandas DataFrame conversion utilities for OSRS Prices API responses."""

import pandas as pd

from osrs_prices.models import (
    AverageResponse,
    LatestResponse,
    MappingResponse,
    TimeseriesResponse,
)


def to_dataframe(
    response: MappingResponse | LatestResponse | AverageResponse | TimeseriesResponse,
) -> pd.DataFrame:
    """Convert an API response to a pandas DataFrame.

    Args:
        response: Any of the API response types.

    Returns:
        A pandas DataFrame with the response data.

    Raises:
        TypeError: If the response type is not supported.

    Examples:
        >>> from osrs_prices import Client
        >>> from osrs_prices.pandas import to_dataframe
        >>> with Client(user_agent="my-app/1.0") as client:
        ...     mapping = client.get_mapping()
        ...     df = to_dataframe(mapping)
    """
    if isinstance(response, MappingResponse):
        return _mapping_to_df(response)
    elif isinstance(response, LatestResponse):
        return _latest_to_df(response)
    elif isinstance(response, AverageResponse):
        return _average_to_df(response)
    elif isinstance(response, TimeseriesResponse):
        return _timeseries_to_df(response)
    else:
        raise TypeError(f"Unsupported response type: {type(response)}")


def _mapping_to_df(response: MappingResponse) -> pd.DataFrame:
    """Convert MappingResponse to DataFrame."""
    records = [item.model_dump() for item in response.items]
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.set_index("id")
    return df


def _latest_to_df(response: LatestResponse) -> pd.DataFrame:
    """Convert LatestResponse to DataFrame."""
    records = []
    for item_id, price in response.data.items():
        record = price.model_dump(by_alias=False)
        record["item_id"] = item_id
        records.append(record)
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.set_index("item_id")
    return df


def _average_to_df(response: AverageResponse) -> pd.DataFrame:
    """Convert AverageResponse to DataFrame."""
    records = []
    for item_id, price in response.data.items():
        record = price.model_dump(by_alias=False)
        record["item_id"] = item_id
        records.append(record)
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.set_index("item_id")
        df.attrs["timestamp"] = response.timestamp
    return df


def _timeseries_to_df(response: TimeseriesResponse) -> pd.DataFrame:
    """Convert TimeseriesResponse to DataFrame."""
    records = [point.model_dump(by_alias=False) for point in response.data]
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.set_index("timestamp")
        df.index = pd.to_datetime(df.index, unit="s", utc=True)
    return df
