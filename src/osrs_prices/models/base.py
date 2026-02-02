"""Base model configuration for all OSRS Prices models."""

from pydantic import BaseModel, ConfigDict


class OSRSBaseModel(BaseModel):
    """Base model with common configuration for all OSRS Prices models."""

    model_config = ConfigDict(
        frozen=True,
        extra="ignore",
        populate_by_name=True,
    )
