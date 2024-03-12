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
from datadoc.enums import DataSetState
from datadoc.enums import DataSetStatus
from datadoc.frontend.fields.display_dataset import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
)
from datadoc.frontend.fields.display_variables import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
)
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
        self.metadata_document: pathlib.Path | CloudPath | None = None
        self.container: model.MetadataContainer | None = None
        self.dataset_path: pathlib.Path | CloudPath | None = None
        self.short_name: str | None = None
        self.dataset = model.Dataset()
        self.variables: list = []
        self.variables_lookup: dict[str, model.Variable] = {}
        if metadata_document_path:
            # In this case the user has specified an independent metadata document for editing
            # without a dataset.
            self.metadata_document = self._open_path(metadata_document_path)
        elif dataset_path:
            self.dataset_path = self._open_path(dataset_path)
            # Build the metadata document path based on the dataset path
            # Example: /path/to/dataset.parquet -> /path/to/dataset__DOC.json
            self.metadata_document = self.dataset_path.parent / (
                self.dataset_path.stem + METADATA_DOCUMENT_FILE_SUFFIX
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

        if (
            self.dataset_path is not None
            and self.dataset == model.Dataset()
            and len(self.variables) == 0
        ):
            self.extract_metadata_from_dataset(self.dataset_path)
            self.dataset.id = uuid.uuid4()
            # Set default values for variables where appropriate
            v: model.Variable
            for v in self.variables:
                if v.variable_role is None:
                    v.variable_role = model.VariableRole.MEASURE
                if v.direct_person_identifying is None:
                    v.direct_person_identifying = False
        if not self.dataset.id:
            self.dataset.id = uuid.uuid4()
        self.variables_lookup = {v.short_name: v for v in self.variables}

    def extract_metadata_from_existing_document(
        self,
        document: pathlib.Path | CloudPath,
    ) -> None:
        """There's an existing metadata document, so read in the metadata from that."""
        fresh_metadata = {}
        try:
            with document.open(mode="r", encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info("Opened existing metadata file %s", document)
            if self.is_metadata_in_container_structure(fresh_metadata):
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
            datadoc_metadata = upgrade_metadata(
                datadoc_metadata,
            )
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

    def is_metadata_in_container_structure(
        self,
        metadata: dict,
    ) -> bool:
        """At a certain point a metadata 'container' was introduced.

        The container provides a structure for different 'types' of metadata, such as 'datadoc', 'pseudonymization' etc.
        This method returns True if the metadata is in the container structure, False otherwise.
        """
        return "datadoc" in metadata

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

        self.dataset = model.Dataset(
            short_name=self.dataset_path.stem if self.dataset_path else None,
            dataset_state=dapla_dataset_path_info.dataset_state,
            dataset_status=DataSetStatus.DRAFT,
            assessment=self.get_assessment_by_state(
                dapla_dataset_path_info.dataset_state,
            ),
            version=dapla_dataset_path_info.dataset_version,
            contains_data_from=str(dapla_dataset_path_info.contains_data_from),
            contains_data_until=str(dapla_dataset_path_info.contains_data_until),
            data_source_path=self.dataset_path,
            metadata_created_by=user_info.get_user_info_for_current_platform().short_email,
            # TODO @mmwinther: Remove multiple_language_support once the model is updated.
            # https://github.com/statisticsnorway/ssb-datadoc-model/issues/41
            subject_field=model.LanguageStringType(
                en=subject_field,
                nb=subject_field,
                nn=subject_field,
            ),
        )
        self.variables = self.ds_schema.get_fields()

    @staticmethod
    def get_assessment_by_state(state: DataSetState | None) -> Assessment | None:
        """Find assessment derived by dataset state."""
        if state is None:
            return None
        match (state):
            case (
                DataSetState.INPUT_DATA
                | DataSetState.PROCESSED_DATA
                | DataSetState.STATISTICS
            ):
                return Assessment.PROTECTED
            case DataSetState.OUTPUT_DATA:
                return Assessment.OPEN
            case _:
                return None

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
