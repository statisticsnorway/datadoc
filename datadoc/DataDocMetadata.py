import datetime
import json
import os
import pathlib
from copy import deepcopy
from typing import Dict, List, Optional

from datadoc.DatasetReader import DatasetReader
from datadoc.DisplayVariables import VariableIdentifiers
from datadoc.Model import (
    DataDocDataSet,
    DataDocVariable,
    MetadataDocument,
)
from datadoc.Enums import (
    AdministrativeStatus,
    DatasetState,
)


class DataDocMetadata:
    def __init__(self, dataset):
        self.dataset = dataset
        self.dataset_full_path = pathlib.Path(self.dataset)
        self.dataset_directory = self.dataset_full_path.resolve().parent
        self.dataset_name = self.dataset_full_path.name
        self.dataset_stem = self.dataset_full_path.stem  # filename without file ending
        self.metadata_document_name = str(self.dataset_stem) + "__DOC.json"
        self.metadata_document_full_path = self.dataset_directory.joinpath(
            self.metadata_document_name
        )
        self.dataset_state = self.get_dataset_state(self.dataset_full_path)
        self.dataset_version = self.get_dataset_version()
        try:
            self.current_user = os.environ["JUPYTERHUB_USER"]
        except KeyError:
            print(
                "JUPYTERHUB_USER env variable not set, using default for current_user"
            )
            self.current_user = "default_user@ssb.no"
        self.current_datetime = str(datetime.datetime.now())

        self.meta: MetadataDocument = MetadataDocument(
            percentage_complete=0,
            document_version=1,
            dataset=DataDocDataSet(),
            variables=[],
        )

        self.variables_lookup: Dict[str, DataDocVariable] = {}

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

    def get_dataset_version(self) -> Optional[str]:
        """Find version information if exists in filename,
        eg. 'v1' in filename 'person_data_v1.parquet'"""
        splitted_file_name = str(self.dataset_stem).split("_")
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
            with open(self.metadata_document_full_path, "r", encoding="utf-8") as JSON:
                fresh_metadata = json.load(JSON)
            print(
                "Opened existing metadata file " + str(self.metadata_document_full_path)
            )

            variables_list = fresh_metadata.pop("variables", None)

            self.meta.variables = [DataDocVariable(**v) for v in variables_list]
            self.meta.dataset = DataDocDataSet(**fresh_metadata)
        else:
            self.generate_new_metadata_document()

        self.variables_lookup = {v.short_name: v for v in self.meta.variables}

    def generate_new_metadata_document(self):
        self.ds_schema = DatasetReader.for_file(self.dataset)

        self.meta.dataset = DataDocDataSet(
            short_name=self.dataset_stem,
            assessment=None,
            dataset_state=self.dataset_state,
            name=None,
            data_source=None,
            population_description=None,
            administrative_status=AdministrativeStatus.DRAFT,
            version=self.dataset_version,
            unit_type=None,
            temporality_type=None,
            description=None,
            spatial_coverage_description=[{"languageCode": "no", "value": "Norge"}],
            id=None,
            owner=None,
            data_source_path=str(self.dataset_full_path),
            created_date=self.current_datetime,
            created_by=self.current_user,
            last_updated_date=None,
            last_updated_by=None,
        )

        self.meta.variables = self.ds_schema.get_fields()

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file"""
        json_str = json.dumps(self.meta.dict(), indent=4, sort_keys=False, default=str)
        self.metadata_document_full_path.write_text(json_str, encoding="utf-8")
