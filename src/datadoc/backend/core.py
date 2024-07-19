"""Handle reading, updating and writing of metadata."""

from __future__ import annotations

import concurrent
import json
import logging
import uuid
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc import config
from datadoc.backend import user_info
from datadoc.backend.constants import DEFAULT_SPATIAL_COVERAGE_DESCRIPTION
from datadoc.backend.constants import NUM_OBLIGATORY_DATASET_FIELDS
from datadoc.backend.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.datadoc_subclass import ValidateDatadocMetadata
from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import (
    is_metadata_in_container_structure,
)
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.backend.utils import calculate_percentage
from datadoc.backend.utils import derive_assessment_from_state
from datadoc.backend.utils import normalize_path
from datadoc.backend.utils import num_obligatory_dataset_fields_completed
from datadoc.backend.utils import num_obligatory_variables_fields_completed
from datadoc.backend.utils import set_default_values_dataset
from datadoc.backend.utils import set_default_values_variables
from datadoc.enums import DataSetStatus
from datadoc.utils import METADATA_DOCUMENT_FILE_SUFFIX
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    import pathlib
    from datetime import datetime

    from cloudpathlib import CloudPath


logger = logging.getLogger(__name__)


class Datadoc:
    """Handle reading, updating and writing of metadata."""

    def __init__(
        self,
        dataset_path: str | None = None,
        metadata_document_path: str | None = None,
        statistic_subject_mapping: StatisticSubjectMapping | None = None,
    ) -> None:
        """Read in a dataset if supplied, otherwise naively instantiate the class."""
        self._statistic_subject_mapping = statistic_subject_mapping
        self.metadata_document: pathlib.Path | CloudPath | None = None
        self.container: model.MetadataContainer | None = None
        self.dataset_path: pathlib.Path | CloudPath | None = None
        self.dataset = model.Dataset()
        self.variables: list = []
        self.variables_lookup: dict[str, model.Variable] = {}
        if metadata_document_path:
            # In this case the user has specified an independent metadata document for editing
            self.metadata_document = normalize_path(metadata_document_path)
        if dataset_path:
            self.dataset_path = normalize_path(dataset_path)
            # Build the metadata document path based on the dataset path if no metadata document is supplied
            # Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json
            if not metadata_document_path:
                self.metadata_document = self.dataset_path.parent / (
                    self.dataset_path.stem + METADATA_DOCUMENT_FILE_SUFFIX
                )
        self._extract_metadata_from_files()

    def _extract_metadata_from_files(self) -> None:
        """Read metadata from an existing metadata document.

        If no metadata document exists, create one from scratch by extracting metadata
        from the dataset file.
        """
        if self.metadata_document is not None and self.metadata_document.exists():
            self._extract_metadata_from_existing_document(self.metadata_document)
        if (
            self.dataset_path is not None
            and self.dataset == model.Dataset()
            and len(self.variables) == 0
        ):
            self._extract_metadata_from_dataset(self.dataset_path)
            self.dataset.id = uuid.uuid4()
            # Set default values for variables where appropriate
            v: model.Variable
            for v in self.variables:
                if v.variable_role is None:
                    v.variable_role = model.VariableRole.MEASURE
        set_default_values_variables(self.variables)
        set_default_values_dataset(self.dataset)
        self.variables_lookup = {v.short_name: v for v in self.variables}

    def _extract_metadata_from_existing_document(
        self,
        document: pathlib.Path | CloudPath,
    ) -> None:
        """There's an existing metadata document, so read in the metadata from that.

        Args:
            document:
                A path to the existing metadata document
        """
        fresh_metadata = {}
        try:
            with document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info("Opened existing metadata file %s", document)
            fresh_metadata = upgrade_metadata(
                fresh_metadata,
            )
            if is_metadata_in_container_structure(fresh_metadata):
                self.container = model.MetadataContainer.model_validate_json(
                    json.dumps(fresh_metadata),
                )
                datadoc_metadata = fresh_metadata["datadoc"]
            else:
                datadoc_metadata = fresh_metadata
            if datadoc_metadata is None:
                # In this case we've read in a file with an empty "datadoc" structure.
                # A typical example of this is a file produced from a pseudonymization process.
                return
            meta = model.DatadocMetadata.model_validate_json(
                json.dumps(datadoc_metadata),
            )
            if meta.dataset is not None:
                self.dataset = meta.dataset
            if meta.variables is not None:
                self.variables = meta.variables
        except json.JSONDecodeError:
            logger.warning(
                "Could not open existing metadata file %s. \
                    Falling back to collecting data from the dataset",
                document,
                exc_info=True,
            )

    def _extract_subject_field_from_path(
        self,
        dapla_dataset_path_info: DaplaDatasetPathInfo,
    ) -> str | None:
        """Extract the statistic short name from the dataset file path.

        Map the extracted statistic short name to its corresponding statistical subject.

        Args:
            dapla_dataset_path_info (DaplaDatasetPathInfo):
                The object representing the decomposed file path

        Returns:
            str | None:
                The code for the statistical subject or None if we couldn't map to one.
        """
        if self._statistic_subject_mapping is None:
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                return StatisticSubjectMapping(
                    executor,
                    config.get_statistical_subject_source_url(),
                ).get_secondary_subject(
                    dapla_dataset_path_info.statistic_short_name,
                )
        else:
            return self._statistic_subject_mapping.get_secondary_subject(
                dapla_dataset_path_info.statistic_short_name,
            )

    def _extract_metadata_from_dataset(
        self,
        dataset: pathlib.Path | CloudPath,
    ) -> None:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according to SSB's standard.
        """
        self.ds_schema: DatasetParser = DatasetParser.for_file(dataset)
        dapla_dataset_path_info = DaplaDatasetPathInfo(dataset)
        self.dataset = model.Dataset(
            short_name=dapla_dataset_path_info.dataset_short_name,
            dataset_state=dapla_dataset_path_info.dataset_state,
            dataset_status=DataSetStatus.DRAFT,
            assessment=(
                derive_assessment_from_state(
                    dapla_dataset_path_info.dataset_state,
                )
                if dapla_dataset_path_info.dataset_state is not None
                else None
            ),
            version=dapla_dataset_path_info.dataset_version,
            contains_data_from=dapla_dataset_path_info.contains_data_from,
            contains_data_until=dapla_dataset_path_info.contains_data_until,
            file_path=str(self.dataset_path),
            metadata_created_by=user_info.get_user_info_for_current_platform().short_email,
            subject_field=self._extract_subject_field_from_path(
                dapla_dataset_path_info,
            ),
            spatial_coverage_description=DEFAULT_SPATIAL_COVERAGE_DESCRIPTION,
        )
        self.variables = self.ds_schema.get_fields()

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file."""
        timestamp: datetime = get_timestamp_now()
        self.dataset.metadata_last_updated_date = timestamp
        self.dataset.metadata_last_updated_by = (
            user_info.get_user_info_for_current_platform().short_email
        )
        self.dataset.file_path = str(self.dataset_path)
        datadoc: ValidateDatadocMetadata = ValidateDatadocMetadata(
            percentage_complete=self.percent_complete,
            dataset=self.dataset,
            variables=self.variables,
        )
        if self.container:
            self.container.datadoc = datadoc
        else:
            self.container = model.MetadataContainer(datadoc=datadoc)
        if self.metadata_document:
            content = self.container.model_dump_json(indent=4)
            self.metadata_document.write_text(content)
            logger.info("Saved metadata document %s", self.metadata_document)
            logger.info("Metadata content:\n%s", content)
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
        num_all_fields = NUM_OBLIGATORY_DATASET_FIELDS
        num_set_fields = num_obligatory_dataset_fields_completed(self.dataset)
        for _i in range(len(self.variables)):
            num_all_fields += NUM_OBLIGATORY_VARIABLES_FIELDS
            num_set_fields += num_obligatory_variables_fields_completed(self.variables)
        return calculate_percentage(num_set_fields, num_all_fields)
