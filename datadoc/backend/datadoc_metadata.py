"""Handle reading, updating and writing of metadata."""
from __future__ import annotations

import json
import logging
import os
import pathlib
import typing as t
import uuid
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.storage_adapter import StorageAdapter
from datadoc.enums import DatasetState, SupportedLanguages, VariableRole
from datadoc.frontend.fields import display_dataset, display_variables
from datadoc.utils import calculate_percentage, get_timestamp_now

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"

PLACEHOLDER_USERNAME = "default_user@ssb.no"


class DataDocMetadata:
    """Handle reading, updating and writing of metadata."""

    def __init__(
        self: t.Self @ DataDocMetadata,
        dataset_path: str | os.PathLike | None = None,
        metadata_document_path: str | os.PathLike | None = None,
    ) -> None:
        """Read in a dataset if supplied, otherwise naively instantiate the class."""
        self.dataset: str = dataset_path
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
            self.extract_metadata_from_existing_document()

        elif self.dataset:
            # The short_name is set as the dataset filename without file extension
            self.short_name: str = pathlib.Path(
                self.dataset,
            ).stem
            self.metadata_document: StorageAdapter = StorageAdapter.for_path(
                StorageAdapter.for_path(self.dataset).parent(),
            )
            self.metadata_document.joinpath(
                self.short_name + METADATA_DOCUMENT_FILE_SUFFIX,
            )
            self.dataset_state: DatasetState = self.get_dataset_state(self.dataset)

            self.extract_metadata_from_files()

        try:
            self.current_user = os.environ["JUPYTERHUB_USER"]
        except KeyError:
            self.current_user = PLACEHOLDER_USERNAME
            logger.warning(
                "JUPYTERHUB_USER env variable not set, using %s as placeholder",
                self.current_user,
            )

    def get_dataset_state(
        self: t.Self @ DataDocMetadata,
        dataset: str,
    ) -> DatasetState | None:
        """Use the path to attempt to guess the state of the dataset."""
        if dataset is None:
            return None
        dataset_path_parts = set(pathlib.Path(dataset).parts)
        for state in DatasetState:
            # We assume that files are saved in the Norwegian language as specified by SSB.
            norwegian_dataset_state_path_part = state.get_value_for_language(
                SupportedLanguages.NORSK_BOKMÅL,
            ).lower()
            norwegian_dataset_state_path_part_variations = {
                norwegian_dataset_state_path_part.replace(" ", x) for x in ["-", "_"]
            }
            # Match on any of the variations anywhere in the path.
            if norwegian_dataset_state_path_part_variations.intersection(
                dataset_path_parts,
            ):
                return state

        return None

    def get_dataset_version(
        self: t.Self @ DataDocMetadata,
        dataset_stem: str,
    ) -> str | None:
        """Find version information if exists in filename.

        eg. 'v1' in filename 'person_data_v1.parquet'
        """
        minimum_elements_in_file_name: t.Final[int] = 2
        minimum_characters_in_version_string: t.Final[int] = 2
        split_file_name = str(dataset_stem).split("_")
        if len(split_file_name) >= minimum_elements_in_file_name:
            last_filename_element = str(split_file_name[-1])
            if (
                len(last_filename_element) >= minimum_characters_in_version_string
                and last_filename_element[0:1] == "v"
                and last_filename_element[1:].isdigit()
            ):
                return last_filename_element[1:]
        return None

    def extract_metadata_from_files(self: t.Self @ DataDocMetadata) -> None:
        """Read metadata from an existing metadata document.

        If no metadata document exists, create one from scratch by extracting metadata
        from the dataset file.
        """
        if self.metadata_document.exists():
            self.extract_metadata_from_existing_document()
        else:
            self.extract_metadata_from_dataset()

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

    def extract_metadata_from_existing_document(self: t.Self @ DataDocMetadata) -> None:
        """There's an existing metadata document, so read in the metadata from that."""
        fresh_metadata = {}
        try:
            with self.metadata_document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info(
                "Opened existing metadata file %s",
                self.metadata_document.location,
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
                self.metadata_document.location,
                exc_info=True,
            )

    def is_metadata_in_container_structure(
        self: t.Self @ DataDocMetadata,
        metadata: dict,
    ) -> bool:
        """At a certain point a metadata 'container' was introduced.

        The container provides a structure for different 'types' of metadata, such as 'datadoc', 'pseudonymization' etc.
        This method returns True if the metadata is in the container structure, False otherwise.
        """
        return "datadoc" in metadata and "dataset" in metadata["datadoc"]

    def extract_metadata_from_dataset(self: t.Self @ DataDocMetadata) -> None:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according to SSB's standard.
        """
        self.ds_schema = DatasetParser.for_file(self.dataset)

        self.meta.dataset = model.Dataset(
            short_name=self.short_name,
            dataset_state=self.dataset_state,
            version=self.get_dataset_version(self.short_name),
            data_source_path=self.dataset,
            created_by=self.current_user,
        )

        self.meta.variables = self.ds_schema.get_fields()

    def write_metadata_document(self: t.Self @ DataDocMetadata) -> None:
        """Write all currently known metadata to file."""
        timestamp: datetime = get_timestamp_now()
        if self.meta.dataset.metadata_created_date is None:
            self.meta.dataset.metadata_created_date = timestamp
        if self.meta.dataset.metadata_created_by is None:
            self.meta.dataset.metadata_created_by = self.current_user
        self.meta.dataset.metadata_last_updated_date = timestamp
        self.meta.dataset.metadata_last_updated_by = self.current_user

        if self.container:
            self.container.datadoc = self.meta
        else:
            self.container = model.MetadataContainer(datadoc=self.meta)

        self.metadata_document.write_text(self.container.model_dump_json(indent=4))
        logger.info("Saved metadata document %s", self.metadata_document.location)

    @property
    def percent_complete(self: t.Self @ DataDocMetadata) -> int:
        """The percentage of obligatory metadata completed.

        A metadata field is counted as complete when any non-None value is
        assigned. Used for a live progress bar in the UI, as well as being
        saved in the datadoc as a simple quality indicator.
        """
        num_all_fields = len(display_dataset.OBLIGATORY_DATASET_METADATA)
        num_set_fields = len(
            [
                k
                for k, v in self.meta.dataset.model_dump().items()
                if k in display_dataset.OBLIGATORY_DATASET_METADATA and v is not None
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
