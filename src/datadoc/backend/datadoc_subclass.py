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


# TODO(@tilen1976): improve these warnings - consider moving to utils or separate warning class  # noqa: TD003
class ValidationWarning(UserWarning):
    """Custom warning for validation purposes."""

    # TODO(@tilen1976): fix issue  # noqa: TD003
    def custom_warning_handler(  # noqa: PLR0913
        message: Warning | str,  # noqa: N805
        category: type[Warning],
        filename: str,
        lineno: int,
        file: TextIO | None = None,  # noqa: ARG002
        line: str | None = None,  # noqa: ARG002
    ) -> None:
        """."""
        print(  # noqa: T201
            f"Warning: {message}, Category: {category.__name__}, Filename: {filename}, Line: {lineno}",
        )

    # Override the default warning handler
    # TODO(@tilen1976): fix issue incompatible types  # noqa: TD003
    warnings.showwarning = custom_warning_handler


class ValidateDatadocMetadata(model.DatadocMetadata):
    """Class inherits from DatadocMetadata providing additional validation.

    Methods:
        check_datae_order:
        check_metadata_created_date(self):
        check_inherit_values(self):
        check_obligatory_dataset_metadata(self):
        check_obligatory_variables_metadata(self):
    """

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        """Run validation check on fields contains_data_from and contains_data_until.

        Raises:
            ValueError: If contains_data_until date is earlier than contains_data_from date.
        Mode:
            after: This validator runs after other validation.
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

    # TODO(@tilen1976): check return value   # noqa: TD003
    @model_validator(mode="after")
    def check_metadata_created_date(self) -> Self:
        """Run validation check on metadata created date.

        Set timestamp value now if value is None value is set by timestamp now.

        Mode:
            after: This validator runs after other validation.
        """
        timestamp: datetime = get_timestamp_now()  # --check-untyped-defs
        if self.dataset is not None and self.dataset.metadata_created_date is None:
            self.dataset.metadata_created_date = timestamp
        return self

    # TODO(@tilen1976): check return value   # noqa: TD003
    @model_validator(mode="after")
    def check_inherit_values(self) -> Self:
        """Check certain variables values for None value.

        Set values on variables if None inherit from dataset values.

        Mode:
            after: This validator runs after other validation.
        """
        if self.variables and self.dataset is not None:
            set_variables_inherit_from_dataset(self.dataset, self.variables)
        return self

    # TODO(@tilen1976): check return value   # noqa: TD003
    @model_validator(mode="after")
    def check_obligatory_dataset_metadata(self) -> Self:
        # TODO(@tilen1976): add docstring   # noqa: TD003
        """.

        Mode:
            after: This validator runs after other validation.
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
                ValidationWarning,
                stacklevel=2,
            )

        return self

    # TODO(@tilen1976): check return value   # noqa: TD003
    @model_validator(mode="after")
    def check_obligatory_variables_metadata(self) -> Self:
        # TODO(@tilen1976): add docstring   # noqa: TD003
        """.

        Mode:
            after: This validator runs after other validation.

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
                ValidationWarning,
                stacklevel=2,
            )

        return self
