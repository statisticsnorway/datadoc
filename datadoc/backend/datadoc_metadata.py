"""Handle reading, updating and writing of metadata."""
from __future__ import annotations

import json
import logging
import os
import pathlib
import typing as t
import uuid
from typing import TYPE_CHECKING

from datadoc_model import Model
from datadoc_model.Enums import DatasetState, SupportedLanguages

from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.storage_adapter import StorageAdapter
from datadoc.frontend.fields import display_dataset, display_variables
from datadoc.utils import calculate_percentage, get_timestamp_now

if TYPE_CHECKING:
    from datetime import datetime

logger = logging.getLogger(__name__)

OBLIGATORY_DATASET_METADATA = [
    m.identifier
    for m in display_dataset.DISPLAY_DATASET.values()
    if m.obligatory and m.editable
]

OBLIGATORY_VARIABLES_METADATA = [
    m.identifier
    for m in display_variables.DISPLAY_VARIABLES.values()
    if m.obligatory and m.editable
]

# These don't vary at runtime so we calculate them as constants here
NUM_OBLIGATORY_DATASET_FIELDS = len(
    [k for k in Model.DataDocDataSet().dict() if k in OBLIGATORY_DATASET_METADATA],
)
NUM_OBLIGATORY_VARIABLES_FIELDS = len(
    [k for k in Model.DataDocVariable().dict() if k in OBLIGATORY_VARIABLES_METADATA],
)

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"

PLACEHOLDER_USERNAME = "default_user@ssb.no"


class DataDocMetadata:
    """Handle reading, updating and writing of metadata."""

    def __init__(
        self: t.Self @ DataDocMetadata,
        dataset: str | None,
    ) -> None:
        """Read in a dataset if supplied, otherwise naively instantiate the class."""
        self.dataset: str = dataset
        if self.dataset:
            self.short_name: str = pathlib.Path(
                self.dataset,
            ).stem  # filename without file ending
            self.metadata_document: StorageAdapter = StorageAdapter.for_path(
                StorageAdapter.for_path(self.dataset).parent(),
            )
            self.metadata_document.joinpath(
                self.short_name + METADATA_DOCUMENT_FILE_SUFFIX,
            )
            self.dataset_state: DatasetState = self.get_dataset_state(self.dataset)
        try:
            self.current_user = os.environ["JUPYTERHUB_USER"]
        except KeyError:
            self.current_user = PLACEHOLDER_USERNAME
            logger.warning(
                "JUPYTERHUB_USER env variable not set, using %s as placeholder",
                self.current_user,
            )

        self.meta: Model.MetadataDocument = Model.MetadataDocument(
            percentage_complete=0,
            document_version=Model.MODEL_VERSION,
            dataset=Model.DataDocDataSet(),
            variables=[],
        )

        self.variables_lookup: dict[str, Model.DataDocVariable] = {}

        if self.dataset:
            self.extract_metadata_from_files()

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
        """Read metadata from a dataset.

        If a metadata document already exists, read in the metadata from that instead.
        """
        fresh_metadata = {}
        if self.metadata_document.exists():
            try:
                with self.metadata_document.open(mode="r", encoding="utf-8") as file:
                    fresh_metadata = json.load(file)
                logger.info(
                    "Opened existing metadata file %s",
                    self.metadata_document.location,
                )

                fresh_metadata = upgrade_metadata(fresh_metadata, Model.MODEL_VERSION)

                variables_list = fresh_metadata.pop("variables", None)

                self.meta.variables = [
                    Model.DataDocVariable(**v) for v in variables_list
                ]
                self.meta.dataset = Model.DataDocDataSet(
                    **fresh_metadata.pop("dataset", None),
                )
            except json.JSONDecodeError:
                logger.warning(
                    "Could not open existing metadata file %s. \
                    Falling back to collecting data from the dataset",
                    self.metadata_document.location,
                    exc_info=True,
                )
                self.extract_metadata_from_dataset()
        else:
            self.extract_metadata_from_dataset()

        if self.meta.dataset.id is None:
            self.meta.dataset.id = uuid.uuid4()

        # Set default values for variables where appropriate
        v: Model.DataDocVariable
        for v in self.meta.variables:
            if v.variable_role is None:
                v.variable_role = Model.Enums.VariableRole.MEASURE
            if v.direct_person_identifying is None:
                v.direct_person_identifying = False

        self.variables_lookup = {v.short_name: v for v in self.meta.variables}

    def extract_metadata_from_dataset(self: t.Self @ DataDocMetadata) -> None:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according to SSB's standard.
        """
        self.ds_schema = DatasetParser.for_file(self.dataset)

        self.meta.dataset = Model.DataDocDataSet(
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
        self.metadata_document.write_text(self.meta.json(indent=4, sort_keys=False))
        logger.info("Saved metadata document %s", self.metadata_document.location)

    @property
    def percent_complete(self: t.Self @ DataDocMetadata) -> int:
        """The percentage of obligatory metadata completed.

        A metadata field is counted as complete when any non-None value is
        assigned. Used for a live progress bar in the UI, as well as being
        saved in the datadoc as a simple quality indicator.
        """
        num_all_fields = NUM_OBLIGATORY_DATASET_FIELDS
        num_set_fields = len(
            [
                k
                for k, v in self.meta.dataset.dict().items()
                if k in OBLIGATORY_DATASET_METADATA and v is not None
            ],
        )

        for variable in self.meta.variables:
            num_all_fields += NUM_OBLIGATORY_VARIABLES_FIELDS
            num_set_fields += len(
                [
                    k
                    for k, v in variable.dict().items()
                    if k in OBLIGATORY_VARIABLES_METADATA and v is not None
                ],
            )

        return calculate_percentage(num_set_fields, num_all_fields)
