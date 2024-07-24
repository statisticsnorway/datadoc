"""Handle reading, updating and writing of metadata."""

from __future__ import annotations

import concurrent
import copy
import json
import logging
import uuid
from typing import TYPE_CHECKING

from datadoc_model import model

from datadoc import config
from datadoc.backend import user_info
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import (
    is_metadata_in_container_structure,
)
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping
from datadoc.backend.utils import DEFAULT_SPATIAL_COVERAGE_DESCRIPTION
from datadoc.backend.utils import calculate_percentage
from datadoc.backend.utils import derive_assessment_from_state
from datadoc.backend.utils import normalize_path
from datadoc.backend.utils import set_default_values_variables
from datadoc.enums import DataSetStatus
from datadoc.frontend.fields.display_dataset import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
)
from datadoc.frontend.fields.display_variables import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
)
from datadoc.utils import METADATA_DOCUMENT_FILE_SUFFIX
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    import pathlib
    from datetime import datetime

    from cloudpathlib import CloudPath


logger = logging.getLogger(__name__)

DATASET_FIELDS_FROM_EXISTING_METADATA = [
    "name",
    "description",
    "dataset_status",
    "data_source",
    "population_description",
    "unit_type",
    "temporality_type",
    "subject_field",
    "keyword",
    "spatial_coverage_description",
]


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
        self.explicitly_defined_metadata_document = False
        if metadata_document_path:
            # In this case the user has specified an independent metadata document for editing
            self.metadata_document = normalize_path(metadata_document_path)
            self.explicitly_defined_metadata_document = True
        if dataset_path:
            self.dataset_path = normalize_path(dataset_path)
            # Build the metadata document path based on the dataset path if no metadata document is supplied
            # Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json
            if not metadata_document_path:
                self.metadata_document = self.dataset_path.parent / (
                    self.dataset_path.stem + METADATA_DOCUMENT_FILE_SUFFIX
                )
        if metadata_document_path or dataset_path:
            self._extract_metadata_from_files()

    def _extract_metadata_from_files(self) -> None:
        """Read metadata from an existing metadata document.

        If no metadata document exists, create one from scratch by extracting metadata
        from the dataset file.
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
        if not self.dataset.id:
            self.dataset.id = uuid.uuid4()
        if self.dataset.contains_personal_data is None:
            self.dataset.contains_personal_data = False
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
        """There's an existing metadata document, so read in the metadata from that.

        Args:
            document: A path to the existing metadata document
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
        """Extract the statistic short name from the dataset file path and map it to its corresponding statistical subject.

        Args:
            dapla_dataset_path_info (DaplaDatasetPathInfo): The object representing the decomposed file path

        Returns:
            str | None: The code for the statistical subject or None if we couldn't map to one.
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
        Certain elements are dependent on the dataset being saved according to SSB's standard.
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
        """Write all currently known metadata to file."""
        timestamp: datetime = get_timestamp_now()

        if self.dataset.metadata_created_date is None:
            self.dataset.metadata_created_date = timestamp
        self.dataset.metadata_last_updated_date = timestamp
        self.dataset.metadata_last_updated_by = (
            user_info.get_user_info_for_current_platform().short_email
        )
        self.dataset.file_path = str(self.dataset_path)

        datadoc: model.DatadocMetadata = model.DatadocMetadata(
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
        num_all_fields = len(OBLIGATORY_DATASET_METADATA_IDENTIFIERS)
        num_set_fields = len(
            [
                k
                for k, v in self.dataset.model_dump().items()
                if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is not None
            ],
        )
        for variable in self.variables:
            num_all_fields += len(OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS)
            num_set_fields += len(
                [
                    k
                    for k, v in variable.model_dump().items()
                    if k in OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS and v is not None
                ],
            )
        return calculate_percentage(num_set_fields, num_all_fields)
