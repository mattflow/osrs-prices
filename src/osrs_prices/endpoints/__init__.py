"""Endpoint classes for the OSRS Prices API."""

from osrs_prices.endpoints.averages import FiveMinuteEndpoint, OneHourEndpoint
from osrs_prices.endpoints.base import BaseEndpoint
from osrs_prices.endpoints.latest import LatestEndpoint
from osrs_prices.endpoints.mapping import MappingEndpoint
from osrs_prices.endpoints.timeseries import TimeseriesEndpoint

__all__ = [
    "BaseEndpoint",
    "FiveMinuteEndpoint",
    "LatestEndpoint",
    "MappingEndpoint",
    "OneHourEndpoint",
    "TimeseriesEndpoint",
]
