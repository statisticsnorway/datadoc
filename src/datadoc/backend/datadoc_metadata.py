"""Handle reading, updating and writing of metadata."""

from __future__ import annotations

import json
import logging
import pathlib
import uuid
from typing import TYPE_CHECKING

from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from dapla import AuthClient
from datadoc_model import model

from datadoc.backend import user_info
from datadoc.backend.dapla_dataset_path_info import DaplaDatasetPathInfo
from datadoc.backend.dataset_parser import DatasetParser
from datadoc.backend.model_backwards_compatibility import upgrade_metadata
from datadoc.enums import Assessment
from datadoc.enums import DatasetState
from datadoc.enums import DatasetStatus
from datadoc.enums import VariableRole
from datadoc.frontend.fields.display_dataset import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
)
from datadoc.frontend.fields.display_variables import OBLIGATORY_VARIABLES_METADATA
from datadoc.utils import METADATA_DOCUMENT_FILE_SUFFIX
from datadoc.utils import calculate_percentage
from datadoc.utils import get_timestamp_now

if TYPE_CHECKING:
    from datetime import datetime

    from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping

logger = logging.getLogger(__name__)


class DataDocMetadata:
    """Handle reading, updating and writing of metadata."""

    def __init__(
        self,
        statistic_subject_mapping: StatisticSubjectMapping,
        dataset_path: str | None = None,
        metadata_document_path: str | None = None,
    ) -> None:
        """Read in a dataset if supplied, otherwise naively instantiate the class."""
        self._statistic_subject_mapping = statistic_subject_mapping
        self.dataset_path = dataset_path

        self.metadata_document: pathlib.Path | CloudPath | None = None
        self.container: model.MetadataContainer | None = None
        self.dataset: pathlib.Path | CloudPath | None = None
        self.short_name: str | None = None
        self.meta: model.DatadocJsonSchema = model.DatadocJsonSchema(
            percentage_complete=0,
            dataset=model.Dataset(),
            variables=[],
        )
        self.variables_lookup: dict[str, model.Variable] = {}
        if metadata_document_path:
            # In this case the user has specified an independent metadata document for editing
            # without a dataset.
            self.metadata_document = self._open_path(metadata_document_path)
            self.extract_metadata_from_existing_document(self.metadata_document)
        elif dataset_path:
            self.dataset = self._open_path(dataset_path)
            # The short_name is set as the dataset filename without file extension
            self.short_name = self.dataset.stem
            # Build the metadata document path based on the dataset path
            # Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json
            self.metadata_document = self.dataset.parent / (
                self.dataset.stem + METADATA_DOCUMENT_FILE_SUFFIX
            )
            self.extract_metadata_from_files()

    @staticmethod
    def _open_path(path: str) -> pathlib.Path | CloudPath:
        """Open a given path regardless of whether it is local or cloud.

        The returned path may be treated just as if it's a pathlib.Path.
        """
        if path.startswith(GSPath.cloud_prefix):
            client = GSClient(credentials=AuthClient.fetch_google_credentials())
            return GSPath(path, client=client)

        return pathlib.Path(path)

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

    def extract_metadata_from_existing_document(
        self,
        document: pathlib.Path | CloudPath,
    ) -> None:
        """There's an existing metadata document, so read in the metadata from that."""
        fresh_metadata = {}
        try:
            with document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info(
                "Opened existing metadata file %s",
                document,
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
                document,
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
        dataset: pathlib.Path | CloudPath,
    ) -> None:
        """Obtain what metadata we can from the dataset itself.

        This makes it easier for the user by 'pre-filling' certain fields.
        Certain elements are dependent on the dataset being saved according to SSB's standard.
        """
        self.ds_schema: DatasetParser = DatasetParser.for_file(dataset)
        dapla_dataset_path_info = DaplaDatasetPathInfo(dataset)

        subject_field = self._statistic_subject_mapping.get_secondary_subject(
            dapla_dataset_path_info.statistic_short_name,
        )

        self.meta.dataset = model.Dataset(
            short_name=self.short_name,
            dataset_state=dapla_dataset_path_info.dataset_state,
            dataset_status=DatasetStatus.DRAFT,
            assessment=self.get_assessment_by_state(
                dapla_dataset_path_info.dataset_state,
            ),
            version=dapla_dataset_path_info.dataset_version,
            contains_data_from=str(dapla_dataset_path_info.contains_data_from),
            contains_data_until=str(dapla_dataset_path_info.contains_data_until),
            data_source_path=self.dataset,
            metadata_created_by=user_info.get_user_info_for_current_platform().short_email,
            # TODO @mmwinther: Remove multiple_language_support once the model is updated.
            # https://github.com/statisticsnorway/ssb-datadoc-model/issues/41
            subject_field=model.LanguageStringType(
                en=subject_field,
                nb=subject_field,
                nn=subject_field,
            ),
        )
        self.meta.variables = self.ds_schema.get_fields()

    @staticmethod
    def get_assessment_by_state(state: DatasetState | None) -> Assessment | None:
        """Find assessment derived by dataset state."""
        if state is None:
            return None
        match (state):
            case (
                DatasetState.INPUT_DATA
                | DatasetState.PROCESSED_DATA
                | DatasetState.STATISTICS
            ):
                return Assessment.PROTECTED
            case DatasetState.OUTPUT_DATA:
                return Assessment.OPEN
            case _:
                return None

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file."""
        timestamp: datetime = get_timestamp_now()

        if self.meta.dataset.metadata_created_date is None:
            self.meta.dataset.metadata_created_date = timestamp
        self.meta.dataset.metadata_last_updated_date = timestamp
        self.meta.dataset.metadata_last_updated_by = (
            user_info.get_user_info_for_current_platform().short_email
        )
        self.meta.dataset.file_path = str(self.dataset)
        if self.container:
            self.container.datadoc = self.meta
        else:
            self.container = model.MetadataContainer(datadoc=self.meta)
        if self.metadata_document:
            self.metadata_document.write_text(self.container.model_dump_json(indent=4))
            logger.info("Saved metadata document %s", self.metadata_document)
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
                for k, v in self.meta.dataset.model_dump().items()
                if k in OBLIGATORY_DATASET_METADATA_IDENTIFIERS and v is not None
            ],
        )
        for variable in self.meta.variables:
            num_all_fields += len(OBLIGATORY_VARIABLES_METADATA)
            num_set_fields += len(
                [
                    k
                    for k, v in variable.model_dump().items()
                    if k in OBLIGATORY_VARIABLES_METADATA and v is not None
                ],
            )
        return calculate_percentage(num_set_fields, num_all_fields)
