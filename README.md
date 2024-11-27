# OSRS Prices

[![PyPI version](https://img.shields.io/pypi/v/osrs-prices.svg)](https://pypi.org/project/osrs-prices/)
[![Python Versions](https://img.shields.io/pypi/pyversions/osrs-prices.svg)](https://pypi.org/project/osrs-prices/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mattflow/osrs-prices/actions/workflows/test.yml/badge.svg)](https://github.com/mattflow/osrs-prices/actions/workflows/test.yml)

A Python client for the RuneScape Wiki Prices API. This library provides easy access to both Old School RuneScape (OSRS) and Deadman Mode (DMM) Grand Exchange prices.

> ⚠️ **Warning:** This project is early in development and should not be relied upon for anything important.

## Installation

Install using pip:

```bash
pip install osrs-prices
```

## Features

- Fetch latest item prices from the RuneScape Wiki API
- Get detailed item mapping data
- Support for both OSRS and DMM game modes
- Optional Pandas DataFrame output
- Type hints and Pydantic models for better development experience

## Quick Start

```python
from osrs_prices import Client

# Initialize the client with your user agent
client = Client(
  user_agent="your-app-name - your@email.com or @discord-handle",
  mode="osrs" # or "dmm". Optional, defaults to "osrs".
)

# Get mapping as a list of Item objects
mapping = client.get_mapping(
  as_pandas=False, # Optional, defaults to False.
  force_refresh=False, # Optional, defaults to False. Mapping does not change often so it is cached
)

# Get mapping as a Pandas DataFrame
mapping_df = client.get_mapping(as_pandas=True)

# Get latest prices as a dictionary mapping of item id to PricePoint objects
latest = client.get_latest(
  as_pandas=False, # Optional, defaults to False.
)

# Get latest prices as a Pandas DataFrame and join with item mapping on item id
latest_df = client.get_latest(
  as_pandas=True,
  mapped=True, # Optional, defaults to False. If as_pandas is False, this parameter is ignored.
  force_refresh=False, # Optional, defaults to False. If as_pandas is False, this parameter is ignored.
)
```
