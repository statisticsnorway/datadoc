"""Classes which inherit from model to extend validation."""

from __future__ import annotations

from typing import Self

from datadoc_model import model
from pydantic import field_validator
from pydantic import model_validator

from datadoc.backend.utils import DATE_VALIDATION_MESSAGE


class DatasetInherit(model.Dataset):  # noqa: D101
    @field_validator("contains_data_until")
    @classmethod
    def check_data_until(cls, value, info):  # noqa: D102, ANN206, ANN001
        message = "contains_data_from must be the same or earlier date than contains_data_until"
        contains_data_from = info.data.get("contains_data_from")
        if contains_data_from is not None and value < contains_data_from:
            raise ValueError(message)
        return value


class ValidateDatadocMetadata(model.DatadocMetadata):
    """."""

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        """."""
        if self.dataset is not None:
            contains_date_from = self.dataset.contains_data_from
            contains_date_until = self.dataset.contains_data_until
            if (
                contains_date_from is not None
                and contains_date_until is not None
                and contains_date_until < contains_date_from
            ):
                raise ValueError(DATE_VALIDATION_MESSAGE)
        return self
