from __future__ import annotations

from typing import TYPE_CHECKING

from datadoc_model import model
from pydantic import field_validator

if TYPE_CHECKING:
    from datetime import date


class ExtendedDataset(model.Dataset):
    """."""

    @field_validator("contains_data_until")
    def validate_contains_data_until(
        self,
        v: date | None,
        values,  # noqa: ANN001
    ) -> date | None:
        """."""
        if (
            v is not None
            and "contains_data_from" in values
            and values["contains_data_from"] is not None
        ) and v <= values["contains_data_from"]:
            msg = "contains_data_until must be after contains_data_from"
            raise ValueError(msg)
        return v
