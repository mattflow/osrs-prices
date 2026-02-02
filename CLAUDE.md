# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

osrs-prices is a typed Python client for the OSRS Real-time Prices API. Uses Python 3.12 with uv as the package manager.

## Commands

```bash
# Install dependencies (use --all-extras to include pandas for DataFrame tests)
uv sync --all-extras

# Run tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit

# Run integration tests (hits real API)
uv run pytest -m integration

# Type checking
uv run mypy src/
```

## Structure

```
src/osrs_prices/
├── __init__.py          # Public exports (Client, models, exceptions)
├── client.py            # Client class - main API interface
├── constants.py         # BASE_URL, timeouts, blocked user agents
├── exceptions.py        # OSRSPricesError, APIError, RateLimitError, ValidationError
├── cache.py             # Thread-safe TTLCache for mapping data
├── pandas.py            # to_dataframe() - requires pandas optional dependency
├── models/
│   ├── base.py          # OSRSBaseModel (frozen, extra="ignore")
│   ├── items.py         # ItemMapping, MappingResponse
│   ├── prices.py        # LatestPrice, LatestResponse, AveragePrice, AverageResponse
│   └── timeseries.py    # TimeseriesDataPoint, TimeseriesResponse, Timestep
└── endpoints/
    ├── base.py          # Abstract BaseEndpoint with error handling
    ├── latest.py        # /latest endpoint
    ├── mapping.py       # /mapping endpoint (with caching)
    ├── averages.py      # /5m and /1h endpoints
    └── timeseries.py    # /timeseries endpoint

tests/
├── conftest.py          # Fixtures with sample API responses
├── unit/                # Unit tests (mocked HTTP)
└── integration/         # Real API tests (marked with @pytest.mark.integration)
```

## Architecture

- **Client**: Main entry point, composes endpoint classes
- **Endpoints**: Each API endpoint is a class extending `BaseEndpoint`
- **Models**: Pydantic models with `frozen=True`, camelCase aliases for API fields
- **Caching**: Only `/mapping` is cached (1-hour TTL, thread-safe)

## Adding a New Endpoint

1. Create model in `models/` with `from_api()` class method
2. Create endpoint class in `endpoints/` extending `BaseEndpoint`
3. Add method to `Client` class
4. Export new models from `models/__init__.py` and `__init__.py`
5. Add tests in `tests/unit/` and `tests/integration/`

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) with automated releases via release-please.

**Format:** `<type>(<scope>): <description>`

**Types:**
- `feat:` - New feature (triggers minor version bump)
- `fix:` - Bug fix (triggers patch version bump)
- `feat!:` or `fix!:` - Breaking change (triggers major version bump)
- `docs:` - Documentation only
- `test:` - Tests only
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

**Examples:**
```bash
git commit -m "feat: add support for /timeseries endpoint"
git commit -m "fix: handle rate limit response correctly"
git commit -m "feat!: rename Client.get_prices to Client.get_latest"
```

**Release workflow:**
1. Merge PRs with conventional commit messages to main
2. release-please automatically creates a Release PR
3. Merge the Release PR to publish to PyPI
