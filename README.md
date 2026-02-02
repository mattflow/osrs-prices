# osrs-prices

A typed Python client for the [OSRS Real-time Prices API](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices).

## Installation

```bash
pip install osrs-prices

# With pandas support
pip install osrs-prices[pandas]
```

## Quick Start

```python
from osrs_prices import Client

with Client(user_agent="my-app/1.0 contact@example.com") as client:
    # Get item metadata
    mapping = client.get_mapping()
    print(f"Loaded {len(mapping.items)} items")

    # Get latest prices
    latest = client.get_latest(item_id=4151)  # Abyssal whip
    whip = latest.data[4151]
    print(f"Abyssal whip: {whip.high:,} gp (instant-buy)")

    # Get price averages
    averages = client.get_5m_average()

    # Get historical data
    timeseries = client.get_timeseries(item_id=4151, timestep="1h")
```

## DataFrame Support

Convert any response to a pandas DataFrame (requires `pip install osrs-prices[pandas]`):

```python
from osrs_prices import Client
from osrs_prices.pandas import to_dataframe

with Client(user_agent="my-app/1.0") as client:
    mapping = client.get_mapping()
    df = to_dataframe(mapping)
    print(df.head())
```

## API Reference

### Client Methods

| Method | Description |
|--------|-------------|
| `get_latest(item_id=None)` | Current instant-buy/sell prices |
| `get_mapping(force_refresh=False)` | Item metadata (cached 1 hour) |
| `get_5m_average(timestamp=None)` | 5-minute price averages |
| `get_1h_average(timestamp=None)` | 1-hour price averages |
| `get_timeseries(item_id, timestep)` | Historical data (timestep: "5m", "1h", "6h", "24h") |
| `get_item_by_name(name)` | Find item by exact name |

### Models

- `LatestPrice` - Instant buy/sell prices with timestamps
- `AveragePrice` - Average prices with volumes
- `ItemMapping` - Item metadata (name, examine, alch values, etc.)
- `TimeseriesDataPoint` - Historical price point

### Exceptions

- `OSRSPricesError` - Base exception
- `APIError` - API returned an error
- `RateLimitError` - Rate limit exceeded (429)
- `ValidationError` - Invalid input (e.g., blocked user agent)

## User-Agent Requirement

The API requires a descriptive User-Agent. Generic agents like `python-requests` are blocked. Use a format like:

```
my-app/1.0 contact@example.com
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run type checking
uv run mypy src/

# Run integration tests (hits real API)
uv run pytest -m integration
```

## License

MIT
