"""Subclass DatadocMetadata."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING
from typing import Self
from typing import TextIO

from datadoc_model import model
from pydantic import model_validator

from datadoc.backend.constants import DATE_VALIDATION_MESSAGE
from datadoc.backend.constants import NUM_OBLIGATORY_DATASET_FIELDS
from datadoc.backend.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from datadoc.backend.utils import get_missing_obligatory_dataset_fields
from datadoc.backend.utils import get_missing_obligatory_variables_fields
from datadoc.backend.utils import incorrect_date_order
from datadoc.backend.utils import num_obligatory_dataset_fields_completed
from datadoc.backend.utils import num_obligatory_variables_fields_completed
from datadoc.backend.utils import set_variables_inherit_from_dataset
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    from datetime import datetime


class ValidateDatadocMetadata(model.DatadocMetadata):
    """Class inherits from DatadocMetadata providing additional validation."""

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        """Run validation check on fields contains_data_from and contains_data_until.

        Raises:
            ValueError: If contains_data_until date is earlier than contains_data_from date.
        Mode:
            after: This validator runs after other validation.

        Returns:
            Self: The instance of the model after validation.
        """
        if self.dataset is not None and incorrect_date_order(
            self.dataset.contains_data_from,
            self.dataset.contains_data_until,
        ):
            raise ValueError(DATE_VALIDATION_MESSAGE)
        if self.variables is not None:
            for v in self.variables:
                if incorrect_date_order(v.contains_data_from, v.contains_data_until):
                    raise ValueError(DATE_VALIDATION_MESSAGE)
        return self

    @model_validator(mode="after")
    def check_metadata_created_date(self) -> Self:
        """Run validation check on metadata created date.

        Set timestamp value if value is None.
        Mode:
            after: This validator runs after other validation.

        Returns:
            Self: The instance of the model after validation.
        """
        timestamp: datetime = get_timestamp_now()  # --check-untyped-defs
        if self.dataset is not None and self.dataset.metadata_created_date is None:
            self.dataset.metadata_created_date = timestamp
        return self

    @model_validator(mode="after")
    def check_inherit_values(self) -> Self:
        """Check variables eligible for inheritence from dataset.

        Set values inherit from dataset on variables 'data source','temporality type','contains data from' and 'contains data until' if values are None.

        Mode:
            after: This validator runs after other validation.

        Returns:
            Self: The instance of the model after validation.
        """
        if self.variables and self.dataset is not None:
            set_variables_inherit_from_dataset(self.dataset, self.variables)
        return self

    @model_validator(mode="after")
    def check_obligatory_dataset_metadata(self) -> Self:
        """Check obligatory dataset fields and return warning if values are missing.

        Raises:
            ValidationWarning: If not all obligatory dataset metadata fields are filled in.

        Stacklevel:
            2: The warning is issued at stack level 2. It will point to this validation function when triggered.

        Mode:
            after: This validator runs after other validation.

        Returns:
            Self: The instance of the model after validation.
        """
        if (
            self.dataset is not None
            and num_obligatory_dataset_fields_completed(
                self.dataset,
            )
            != NUM_OBLIGATORY_DATASET_FIELDS
        ):
            warnings.warn(
                f"All obligatory metadata is not filled in for dataset {get_missing_obligatory_dataset_fields(self.dataset)}",
                ObligatoryDatasetWarning,
                stacklevel=2,
            )

        return self

    @model_validator(mode="after")
    def check_obligatory_variables_metadata(self) -> Self:
        """Check obligatory variable fields and return warning if values are missing.

        Raises:
            ValidationWarning: If not all obligatory variable metadata fields are filled in.

        Stacklevel:
            2: The warning is issued at stack level 2. It will point to this validation function when triggered.

        Mode:
            after: This validator runs after other validation.

        Returns:
            Self: The instance of the model after validation.
        """
        if (
            self.variables is not None
            and num_obligatory_variables_fields_completed(
                self.variables,
            )
            != NUM_OBLIGATORY_VARIABLES_FIELDS
        ):
            warnings.warn(
                f"All obligatory metadata is not filled in for variables {get_missing_obligatory_variables_fields(self.variables)}",
                ObligatoryVariableWarning,
                stacklevel=2,
            )

        return self


class ValidateDataset(model.Dataset):
    """Class inherits from model.Dataset providing additional validation."""


class ValidationWarning(UserWarning):
    """Custom warning for validation purposes."""


class ObligatoryDatasetWarning(UserWarning):
    """Custom warning for checking obligatory metadata for dataset."""


class ObligatoryVariableWarning(UserWarning):
    """Custom warning for checking obligatory metadata for dataset."""


def custom_warning_handler(  # noqa: PLR0913 remove fields causes incompatible types
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,  # noqa: ARG001 remove causes incompatible types
    line: str | None = None,  # noqa: ARG001 remove causes incompatible types
) -> None:
    """Handle warnings."""
    print(  # noqa: T201
        f"Warning: {message}, Category: {category.__name__}, Filename: {filename}, Line: {lineno}",
    )


warnings.showwarning = custom_warning_handler
