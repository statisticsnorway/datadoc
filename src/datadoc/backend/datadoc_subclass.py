"""Classes which inherit from model to extend validation."""

from __future__ import annotations

from typing import Self

from datadoc_model import model
from pydantic import model_validator

from datadoc.backend.utils import DATE_VALIDATION_MESSAGE


class ValidateDatadocMetadata(model.DatadocMetadata):
    """Inherits from DatadocMetadata and provides additional functionality for validation of DatadocMetadata."""

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        """Runs validation check on fields contains_data_from and contains_data_until to ensure contains_data_until is equal or after contains_data_from.

        Raises:
            ValueError
        Mode: After...
        """
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
