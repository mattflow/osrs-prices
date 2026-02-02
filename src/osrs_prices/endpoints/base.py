"""Base endpoint class for all API endpoints."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

import httpx

from osrs_prices.constants import BASE_URL
from osrs_prices.exceptions import APIError, RateLimitError

T = TypeVar("T")


class BaseEndpoint(ABC, Generic[T]):
    """Abstract base class for API endpoints."""

    path: str

    def __init__(self, client: httpx.Client) -> None:
        """Initialize the endpoint.

        Args:
            client: The httpx client to use for requests.
        """
        self._client = client

    @abstractmethod
    def _parse_response(self, data: Any) -> T:
        """Parse the API response into the appropriate model.

        Args:
            data: The raw JSON data from the API.

        Returns:
            The parsed model instance.
        """

    def _request(self, params: dict[str, Any] | None = None) -> T:
        """Make a request to the endpoint.

        Args:
            params: Optional query parameters.

        Returns:
            The parsed response model.

        Raises:
            RateLimitError: If the API returns a 429 status.
            APIError: If the API returns any other error status.
        """
        url = f"{BASE_URL}{self.path}"
        response = self._client.get(url, params=params)

        if response.status_code == 429:
            raise RateLimitError()

        if response.status_code != 200:
            raise APIError(
                f"API request failed: {response.status_code} {response.text}",
                status_code=response.status_code,
            )

        return self._parse_response(response.json())
