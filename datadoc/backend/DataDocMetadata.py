import datetime
import json
import logging
import os
import pathlib
from typing import Dict, Optional

from datadoc_model import Model
from datadoc_model.Enums import DatasetState

import datadoc.frontend.fields.DisplayDataset as DisplayDataset
import datadoc.frontend.fields.DisplayVariables as DisplayVariables
from datadoc.backend.DatasetParser import DatasetParser
from datadoc.backend.StorageAdapter import StorageAdapter
from datadoc.utils import calculate_percentage

logger = logging.getLogger(__name__)

OBLIGATORY_DATASET_METADATA = [
    m.identifier for m in DisplayDataset.DISPLAY_DATASET.values() if m.obligatory
]

OBLIGATORY_VARIABLES_METADATA = [
    m.identifier for m in DisplayVariables.DISPLAY_VARIABLES.values() if m.obligatory
]

# These don't vary at runtime so we calculate them as constants here
NUM_OBLIGATORY_DATASET_FIELDS = len(
    [
        k
        for k in Model.DataDocDataSet().dict().keys()
        if k in OBLIGATORY_DATASET_METADATA
    ]
)
NUM_OBLIGATORY_VARIABLES_FIELDS = len(
    [
        k
        for k in Model.DataDocVariable().dict().keys()
        if k in OBLIGATORY_VARIABLES_METADATA
    ]
)

METADATA_DOCUMENT_FILE_SUFFIX = "__DOC.json"


class DataDocMetadata:
    def __init__(self, dataset):
        self.dataset: str = dataset
        self.short_name: str = pathlib.Path(
            self.dataset
        ).stem  # filename without file ending
        self.metadata_document: StorageAdapter = StorageAdapter.for_path(
            StorageAdapter.for_path(self.dataset).parent()
        )
        self.metadata_document.joinpath(self.short_name + METADATA_DOCUMENT_FILE_SUFFIX)
        self.dataset_state: DatasetState = self.get_dataset_state(self.dataset)
        try:
            self.current_user = os.environ["JUPYTERHUB_USER"]
        except KeyError:
            self.current_user = "default_user@ssb.no"
            logger.warning(
                f"JUPYTERHUB_USER env variable not set, using {self.current_user} as placeholder"
            )
        self.current_datetime = str(datetime.datetime.now())

        self.meta: "Model.MetadataDocument" = Model.MetadataDocument(
            percentage_complete=0,
            document_version=1,
            dataset=Model.DataDocDataSet(),
            variables=[],
        )

        self.variables_lookup: Dict[str, "Model.DataDocVariable"] = {}

        self.read_metadata_document()

    def get_dataset_state(self, dataset: str) -> Optional[DatasetState]:
        """Use the path to attempt to guess the state of the dataset"""
        if dataset is None:
            return None
        dataset_path_parts = list(pathlib.Path(dataset).parts)
        if "utdata" in dataset_path_parts:
            return DatasetState.OUTPUT_DATA
        elif "statistikk" in dataset_path_parts:
            return DatasetState.STATISTIC
        elif "klargjorte-data" in dataset_path_parts:
            return DatasetState.PROCESSED_DATA
        elif "klargjorte_data" in dataset_path_parts:
            return DatasetState.PROCESSED_DATA
        elif "kildedata" in dataset_path_parts:
            return DatasetState.SOURCE_DATA
        elif "inndata" in dataset_path_parts:
            return DatasetState.INPUT_DATA
        else:
            return None

    def get_dataset_version(self, dataset_stem: str) -> Optional[str]:
        """Find version information if exists in filename,
        eg. 'v1' in filename 'person_data_v1.parquet'"""
        splitted_file_name = str(dataset_stem).split("_")
        if len(splitted_file_name) >= 2:
            last_filename_element = str(splitted_file_name[-1])
            if (
                len(last_filename_element) >= 2
                and last_filename_element[0:1] == "v"
                and last_filename_element[1:].isdigit()
            ):
                return last_filename_element[1:]
        return None

    def read_metadata_document(self):
        fresh_metadata = {}
        if self.metadata_document.exists():
            try:
                with self.metadata_document.open(mode="r", encoding="utf-8") as file:
                    fresh_metadata = json.load(file)
                logger.info(
                    f"Opened existing metadata file {self.metadata_document.location}"
                )

                variables_list = fresh_metadata.pop("variables", None)

                self.meta.variables = [
                    Model.DataDocVariable(**v) for v in variables_list
                ]
                self.meta.dataset = Model.DataDocDataSet(
                    **fresh_metadata.pop("dataset", None)
                )
            except json.JSONDecodeError:
                logger.warning(
                    f"Could not open existing metadata file {self.metadata_document.location}. \
                    Falling back to collecting data from the dataset",
                    exc_info=True,
                )
                self.extract_metadata_from_dataset()
        else:
            self.extract_metadata_from_dataset()

        self.variables_lookup = {v.short_name: v for v in self.meta.variables}

    def extract_metadata_from_dataset(self):
        self.ds_schema = DatasetParser.for_file(self.dataset)

        self.meta.dataset = Model.DataDocDataSet(
            short_name=self.short_name,
            dataset_state=self.dataset_state,
            version=self.get_dataset_version(self.short_name),
            data_source_path=self.dataset,
            created_date=self.current_datetime,
            created_by=self.current_user,
        )

        self.meta.variables = self.ds_schema.get_fields()

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file"""
        self.metadata_document.write_text(self.meta.json(indent=4, sort_keys=False))
        logger.info(f"Saved metadata document {self.metadata_document.location}")

    @property
    def percent_complete(self) -> int:
        """The percentage of obligatory metadata completed.

        A metadata field is counted as complete when any non-None value is
        assigned. Used for a live progress bar in the UI, as well as being
        saved in the datadoc as a simple quality indicator."""

        num_all_fields = NUM_OBLIGATORY_DATASET_FIELDS
        num_set_fields = len(
            [
                k
                for k, v in self.meta.dataset.dict().items()
                if k in OBLIGATORY_DATASET_METADATA and v is not None
            ]
        )

        for variable in self.meta.variables:
            num_all_fields += NUM_OBLIGATORY_VARIABLES_FIELDS
            num_set_fields += len(
                [
                    k
                    for k, v in variable.dict().items()
                    if k in OBLIGATORY_VARIABLES_METADATA and v is not None
                ]
            )

        return calculate_percentage(num_set_fields, num_all_fields)
