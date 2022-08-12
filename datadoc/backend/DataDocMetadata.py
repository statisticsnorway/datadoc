import datetime
import json
import logging
import os
import pathlib
from typing import Dict, Optional

import datadoc.frontend.fields.DisplayDataset as DisplayDataset
import datadoc.frontend.fields.DisplayVariables as DisplayVariables
from datadoc.backend.DatasetReader import DatasetReader
from datadoc.utils import calculate_percentage
from datadoc_model import Model
from datadoc_model.Enums import DatasetState

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


class DataDocMetadata:
    def __init__(self, dataset):
        self.dataset = dataset
        self.dataset_full_path = pathlib.Path(self.dataset)
        self.dataset_directory = self.dataset_full_path.resolve().parent
        self.dataset_stem = self.dataset_full_path.stem  # filename without file ending
        self.metadata_document_name = str(self.dataset_stem) + "__DOC.json"
        self.metadata_document_full_path = self.dataset_directory.joinpath(
            self.metadata_document_name
        )
        self.dataset_state: DatasetState = self.get_dataset_state(
            self.dataset_full_path
        )
        self.dataset_version = self.get_dataset_version(self.dataset_stem)
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

    def get_dataset_state(
        self, dataset_path: pathlib.Path = None
    ) -> Optional[DatasetState]:
        """Use the path to attempt to guess the state of the dataset"""

        if dataset_path is None:
            dataset_path = self.dataset_full_path
        dataset_path_parts = list(dataset_path.parts)
        if "kildedata" in dataset_path_parts:
            return DatasetState.SOURCE_DATA
        elif "inndata" in dataset_path_parts:
            return DatasetState.INPUT_DATA
        elif "klargjorte_data" in dataset_path_parts:
            return DatasetState.PROCESSED_DATA
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
        if self.metadata_document_full_path.exists():
            with open(self.metadata_document_full_path, encoding="utf-8") as file:
                fresh_metadata = json.load(file)
            logger.info(
                f"Opened existing metadata file {self.metadata_document_full_path}"
            )

            variables_list = fresh_metadata.pop("variables", None)

            self.meta.variables = [Model.DataDocVariable(**v) for v in variables_list]
            self.meta.dataset = Model.DataDocDataSet(
                **fresh_metadata.pop("dataset", None)
            )
        else:
            self.generate_new_metadata_document()

        self.variables_lookup = {v.short_name: v for v in self.meta.variables}

    def generate_new_metadata_document(self):
        self.ds_schema = DatasetReader.for_file(self.dataset)

        self.meta.dataset = Model.DataDocDataSet(
            short_name=self.dataset_stem,
            dataset_state=self.dataset_state,
            version=self.dataset_version,
            data_source_path=str(self.dataset_full_path),
            created_date=self.current_datetime,
            created_by=self.current_user,
        )

        self.meta.variables = self.ds_schema.get_fields()

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file"""
        self.metadata_document_full_path.write_text(
            self.meta.json(indent=4, sort_keys=False), encoding="utf-8"
        )
        logger.info(f"Saved metadata document {self.metadata_document_full_path}")

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
