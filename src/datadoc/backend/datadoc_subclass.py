"""Subclass DatadocMetadata.."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Self

from datadoc_model import model
from pydantic import model_validator

from datadoc.backend.utils import DATE_VALIDATION_MESSAGE
from datadoc.backend.utils import set_variables_inherit_from_dataset
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    from datetime import datetime


class ValidateDatadocMetadata(model.DatadocMetadata):
    """Inherit from DatadocMetadata and provide additional validation."""

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        """Run validation check on fields contains_data_from and contains_data_until.

        Raises:
            ValueError: If contains_data_until date is earlier than contains_data_from date.
        Mode:
            after: This validator runs after other validation.
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

    @model_validator(mode="after")
    def check_metadata_created_date(self) -> Self:
        """."""
        timestamp: datetime = get_timestamp_now()  # --check-untyped-defs
        if self.dataset is not None and self.dataset.metadata_created_date is None:
            self.dataset.metadata_created_date = timestamp
        return self

    @model_validator(mode="after")
    def check_inherit_values(self) -> Self:
        """Check certain variables values for None value.

        Set values on variables if None inherit from dataset values.

        Mode:
            after:

        """
        if self.variables and self.dataset is not None:
            set_variables_inherit_from_dataset(self.dataset, self.variables)
        return self
