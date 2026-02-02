"""Constants for the OSRS Prices API client."""

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"

DEFAULT_TIMEOUT = 30.0
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

BLOCKED_USER_AGENTS = frozenset({
    "python-requests",
    "python-httpx",
    "aiohttp",
    "urllib",
})
