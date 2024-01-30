"""Handle reading, updating and writing of metadata."""
from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc import config
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.storage_adapter import StorageAdapter
from datadoc.enums import DatasetState
from datadoc.enums import VariableRole
from datadoc.frontend.fields import display_dataset
from datadoc.frontend.fields import display_variables
from datadoc.utils import calculate_percentage
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    import os
    from datetime import datetime

logger = logging.getLogger(__name__)

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"

PLACEHOLDER_USERNAME = "default_user@ssb.no"


class DataDocMetadata:
    """Handle reading, updating and writing of metadata."""

    def __init__(
        self,
        dataset_path: str | os.PathLike[str] | None = None,
        metadata_document_path: str | os.PathLike[str] | None = None,
    ) -> None:
        """Read in a dataset if supplied, otherwise naively instantiate the class."""
        self.dataset: pathlib.Path | None = None
        self.metadata_document: StorageAdapter | None = None
        self.container: model.MetadataContainer | None = None

        self.dataset_state: DatasetState | None = None
        self.short_name: str | None = None
        self.current_user: str | None = None
        self.meta: model.DatadocJsonSchema = model.DatadocJsonSchema(
            percentage_complete=0,
            dataset=model.Dataset(),
            variables=[],
        )

        self.variables_lookup: dict[str, model.Variable] = {}

        if metadata_document_path:
            # In this case the user has specified an independent metadata document for editing
            # without a dataset.
            self.metadata_document = StorageAdapter.for_path(metadata_document_path)
            self.extract_metadata_from_existing_document(self.metadata_document)

        elif dataset_path:
            # This is the most common use case.
            self.dataset = pathlib.Path(dataset_path)
            # The short_name is set as the dataset filename without file extension
            self.short_name = pathlib.Path(
                self.dataset,
            ).stem
            self.metadata_document = StorageAdapter.for_path(
                StorageAdapter.for_path(self.dataset).parent(),
            )
            self.metadata_document.joinpath(
                self.short_name + METADATA_DOCUMENT_FILE_SUFFIX,
            )

            self.extract_metadata_from_files()

        self.current_user = config.get_jupyterhub_user()
        if not self.current_user:
            self.current_user = PLACEHOLDER_USERNAME
            logger.warning(
                "JUPYTERHUB_USER env variable not set, using %s as placeholder",
                self.current_user,
            )

    def extract_metadata_from_files(self) -> None:
        """Read metadata from an existing metadata document.

        If no metadata document exists, create one from scratch by extracting metadata
        from the dataset file.
        """
        if self.metadata_document is not None and self.metadata_document.exists():
            self.extract_metadata_from_existing_document(self.metadata_document)
        elif self.dataset is not None:
            self.extract_metadata_from_dataset(self.dataset)

            self.meta.dataset.id = uuid.uuid4()

            # Set default values for variables where appropriate
            v: model.Variable
            for v in self.meta.variables:
                if v.variable_role is None:
                    v.variable_role = VariableRole.MEASURE
                if v.direct_person_identifying is None:
                    v.direct_person_identifying = False

        if not self.meta.dataset.id:
            self.meta.dataset.id = uuid.uuid4()

        self.variables_lookup = {v.short_name: v for v in self.meta.variables}

    def extract_metadata_from_existing_document(self, document: StorageAdapter) -> None:
        """There's an existing metadata document, so read in the metadata from that."""
        fresh_metadata = {}
        try:
            with document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info(
                "Opened existing metadata file %s",
                document.location,
            )

            if self.is_metadata_in_container_structure(fresh_metadata):
                self.container = model.MetadataContainer.model_validate_json(
                    json.dumps(fresh_metadata),
                )
                datadoc_metadata = fresh_metadata["datadoc"]
            else:
                datadoc_metadata = fresh_metadata

            datadoc_metadata = upgrade_metadata(
                datadoc_metadata,
            )

            self.meta = model.DatadocJsonSchema.model_validate_json(
                json.dumps(datadoc_metadata),
            )

        except json.JSONDecodeError:
            logger.warning(
                "Could not open existing metadata file %s. \
                    Falling back to collecting data from the dataset",
                document.location,
                exc_info=True,
            )

    def is_metadata_in_container_structure(
        self,
        metadata: dict,
    ) -> bool:
        """At a certain point a metadata 'container' was introduced.

        The container provides a structure for different 'types' of metadata, such as 'datadoc', 'pseudonymization' etc.
        This method returns True if the metadata is in the container structure, False otherwise.
        """
        return "datadoc" in metadata and "dataset" in metadata["datadoc"]

    def extract_metadata_from_dataset(
        self,
        dataset: pathlib.Path,
    ) -> None:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according to SSB's standard.
        """
        self.ds_schema: DatasetParser = DatasetParser.for_file(dataset)

        dapla_dataset_path_info = DaplaDatasetPathInfo(dataset)

        self.meta.dataset = model.Dataset(
            short_name=self.short_name,
            dataset_state=dapla_dataset_path_info.dataset_state,
            version=dapla_dataset_path_info.dataset_version,
            contains_data_from=str(dapla_dataset_path_info.contains_data_from),
            contains_data_until=str(dapla_dataset_path_info.contains_data_until),
            data_source_path=self.dataset,
            created_by=self.current_user,
        )

        self.meta.variables = self.ds_schema.get_fields()

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file."""
        timestamp: datetime = get_timestamp_now()
        if self.meta.dataset.metadata_created_date is None:
            self.meta.dataset.metadata_created_date = timestamp
        if self.meta.dataset.metadata_created_by is None:
            self.meta.dataset.metadata_created_by = self.current_user
        self.meta.dataset.metadata_last_updated_date = timestamp
        self.meta.dataset.metadata_last_updated_by = self.current_user
        self.meta.dataset.file_path = str(self.dataset)
        if self.container:
            self.container.datadoc = self.meta
        else:
            self.container = model.MetadataContainer(datadoc=self.meta)

        if self.metadata_document:
            self.metadata_document.write_text(self.container.model_dump_json(indent=4))
            logger.info("Saved metadata document %s", self.metadata_document.location)
        else:
            msg = "No metadata document to save"
            raise ValueError(msg)

    @property
    def percent_complete(self) -> int:
        """The percentage of obligatory metadata completed.

        A metadata field is counted as complete when any non-None value is
        assigned. Used for a live progress bar in the UI, as well as being
        saved in the datadoc as a simple quality indicator.
        """
        num_all_fields = len(display_dataset.OBLIGATORY_DATASET_METADATA_IDENTIFIERS)
        num_set_fields = len(
            [
                k
                for k, v in self.meta.dataset.model_dump().items()
                if k in display_dataset.OBLIGATORY_DATASET_METADATA_IDENTIFIERS
                and v is not None
            ],
        )

        for variable in self.meta.variables:
            num_all_fields += len(display_variables.OBLIGATORY_VARIABLES_METADATA)
            num_set_fields += len(
                [
                    k
                    for k, v in variable.model_dump().items()
                    if k in display_variables.OBLIGATORY_VARIABLES_METADATA
                    and v is not None
                ],
            )

        return calculate_percentage(num_set_fields, num_all_fields)
