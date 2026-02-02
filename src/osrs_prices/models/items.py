"""Models for item mapping data."""

from typing import Any

from pydantic import Field

from osrs_prices.models.base import OSRSBaseModel


class ItemMapping(OSRSBaseModel):
    """Represents metadata for a single item."""

    id: int
    name: str
    examine: str | None = None
    members: bool
    lowalch: int | None = None
    highalch: int | None = None
    limit: int | None = None
    value: int | None = None
    icon: str


class MappingResponse(OSRSBaseModel):
    """Response from the /mapping endpoint."""

    items: list[ItemMapping] = Field(default_factory=list)

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> "MappingResponse":
        """Create a MappingResponse from a list of item dicts.

        The API returns a raw list, not a wrapped object.
        """
        items = [ItemMapping.model_validate(item) for item in data]
        return cls(items=items)
