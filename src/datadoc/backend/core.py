"""Handle reading, updating and writing of metadata."""

from __future__ import annotations

import concurrent
import copy
import json
import logging
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc import config
from datadoc.backend import user_info
from datadoc.backend.constants import DATASET_FIELDS_FROM_EXISTING_METADATA
from datadoc.backend.constants import DEFAULT_SPATIAL_COVERAGE_DESCRIPTION
from datadoc.backend.constants import NUM_OBLIGATORY_DATASET_FIELDS
from datadoc.backend.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import (
    is_metadata_in_container_structure,
)
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.model_validation import ValidateDatadocMetadata
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
    """Handle reading, updating and writing of metadata.

    If a metadata document exists, it is this information that is loaded. Nothing
    is inferred from the dataset. If only a dataset path is supplied the metadata
    document path is build based on the dataset path.

    Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json

    Attributes:
        dataset_path: A file path to the path to where the dataset is stored.
        metadata_document_path: A path to a metadata document if it exists.
        statistic_subject_mapping: An instance of StatisticSubjectMapping.
    """

    def __init__(
        self,
        dataset_path: str | None = None,
        metadata_document_path: str | None = None,
        statistic_subject_mapping: StatisticSubjectMapping | None = None,
    ) -> None:
        """Initialize the Datadoc instance.

        If a dataset path is supplied, it attempts to locate and load the
        corresponding metadata document. If no dataset path is provided, the class
        is instantiated without loading any metadata.

        Args:
            dataset_path: The file path to the dataset. Defaults to None.
            metadata_document_path: The file path to the metadata document.
                Defaults to None.
            statistic_subject_mapping: An instance of StatisticSubjectMapping.
                Defaults to None.
        """
        self._statistic_subject_mapping = statistic_subject_mapping
        self.metadata_document: pathlib.Path | CloudPath | None = None
        self.container: model.MetadataContainer | None = None
        self.dataset_path: pathlib.Path | CloudPath | None = None
        self.dataset = model.Dataset()
        self.variables: list = []
        self.variables_lookup: dict[str, model.Variable] = {}
        self.explicitly_defined_metadata_document = False
        if metadata_document_path:
            self.metadata_document = normalize_path(metadata_document_path)
            self.explicitly_defined_metadata_document = True
        if dataset_path:
            self.dataset_path = normalize_path(dataset_path)
            if not metadata_document_path:
                self.metadata_document = self.dataset_path.parent / (
                    self.dataset_path.stem + METADATA_DOCUMENT_FILE_SUFFIX
                )
        if metadata_document_path or dataset_path:
            self._extract_metadata_from_files()

    def _extract_metadata_from_files(self) -> None:
        """Read metadata from an existing metadata document or create one.

        If a metadata document exists, it reads and extracts metadata from it.
        If no metadata document is found, it creates metadata from scratch by
        extracting information from the dataset file.

        This method ensures that:
        - Metadata is extracted from an existing document if available.
        - If metadata is not available, it is extracted from the dataset file.
        - The dataset ID is set if not already present.
        - Default values are set for variables, particularly the variable role on
            creation.
        - Default values for variables ID and 'is_personal_data' are set if the
            values are None.
        - The 'contains_personal_data' attribute is set to False if not specified.
        - A lookup dictionary for variables is created based on their short names.
        """
        extracted_metadata: model.DatadocMetadata | None = None
        existing_metadata: model.DatadocMetadata | None = None
        if self.metadata_document is not None and self.metadata_document.exists():
            existing_metadata = self._extract_metadata_from_existing_document(
                self.metadata_document,
            )
        if (
            self.dataset_path is not None
            and self.dataset == model.Dataset()
            and len(self.variables) == 0
        ):
            extracted_metadata = self._extract_metadata_from_dataset(self.dataset_path)

        if self.dataset_path and self.explicitly_defined_metadata_document:
            merged_metadata = self._merge_metadata(
                extracted_metadata,
                existing_metadata,
            )
            if merged_metadata.dataset and merged_metadata.variables:
                self.dataset = merged_metadata.dataset
                self.variables = merged_metadata.variables
            else:
                msg = "Could not read metadata"
                raise ValueError(msg)
        elif (
            existing_metadata
            and existing_metadata.dataset
            and existing_metadata.variables
        ):
            self.dataset = existing_metadata.dataset
            self.variables = existing_metadata.variables
        elif (
            extracted_metadata
            and extracted_metadata.dataset
            and extracted_metadata.variables
        ):
            self.dataset = extracted_metadata.dataset
            self.variables = extracted_metadata.variables
        else:
            msg = "Could not read metadata"
            raise ValueError(msg)
        set_default_values_variables(self.variables)
        set_default_values_dataset(self.dataset)
        self.variables_lookup = {
            v.short_name: v for v in self.variables if v.short_name
        }

    @staticmethod
    def _merge_metadata(
        extracted_metadata: model.DatadocMetadata | None,
        existing_metadata: model.DatadocMetadata | None,
    ) -> model.DatadocMetadata:
        # Use the extracted metadata as a base or an empty structure if extracted_metadata is None
        merged_metadata = copy.deepcopy(extracted_metadata)
        if not existing_metadata:
            logger.warning(
                "No existing metadata found, no merge to perform. Continuing with extracted metadata.",
            )
            return merged_metadata or model.DatadocMetadata()
        if not merged_metadata:
            return existing_metadata
        if (
            merged_metadata.dataset is not None
            and existing_metadata.dataset is not None
        ):
            # Override the fields as defined
            for field in DATASET_FIELDS_FROM_EXISTING_METADATA:
                setattr(
                    merged_metadata.dataset,
                    field,
                    getattr(existing_metadata.dataset, field),
                )
        return merged_metadata

    def _extract_metadata_from_existing_document(
        self,
        document: pathlib.Path | CloudPath,
    ) -> model.DatadocMetadata | None:
        """Read metadata from an existing metadata document.

        If an existing metadata document is available, this method reads and loads
        the metadata from it. It validates and upgrades the metadata as necessary.
        If we have read in a file with an empty "datadoc" structure the process ends.
        A typical example causing a empty datadoc is a file produced from a
        pseudonymization process.

        Args:
            document: A path to the existing metadata document.

        Raises:
            json.JSONDecodeError: If the metadata document cannot be parsed.
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
                return None
            return model.DatadocMetadata.model_validate_json(
                json.dumps(datadoc_metadata),
            )
        except json.JSONDecodeError:
            logger.warning(
                "Could not open existing metadata file %s. \
                    Falling back to collecting data from the dataset",
                document,
                exc_info=True,
            )
            return None

    def _extract_subject_field_from_path(
        self,
        dapla_dataset_path_info: DaplaDatasetPathInfo,
    ) -> str | None:
        """Extract the statistic short name from the dataset file path.

        Map the extracted statistic short name to its corresponding statistical
        subject.

        Args:
            dapla_dataset_path_info: The object representing the decomposed file
                path.

        Returns:
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
    ) -> model.DatadocMetadata:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according
        to SSB's standard.

        Args:
            dataset: The path to the dataset file, which can be a local or
                cloud path.

        Side Effects:
            Updates the following instance attributes:
                - ds_schema: An instance of DatasetParser initialized for the
                    given dataset file.
                - dataset: An instance of model.Dataset with pre-filled metadata
                    fields.
                - variables: A list of fields extracted from the dataset schema.
        """
        dapla_dataset_path_info = DaplaDatasetPathInfo(dataset)
        metadata = model.DatadocMetadata()

        metadata.dataset = model.Dataset(
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
        metadata.variables = DatasetParser.for_file(dataset).get_fields()
        return metadata

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file.

        Side Effects:
            - Updates the dataset's metadata_last_updated_date and
                metadata_last_updated_by attributes.
            - Updates the dataset's file_path attribute.
            - Validates the metadata model and stores it in a MetadataContainer.
            - Writes the validated metadata to a file if the metadata_document
                attribute is set.
            - Logs the action and the content of the metadata document.

        Raises:
            ValueError: If no metadata document is specified for saving.
        """
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
