from copy import deepcopy
import json
import pathlib
import datetime
import os
from typing import Dict, List, Optional
from DisplayVariables import VariableIdentifiers

from Model import (
    AdministrativeStatus,
    DataDocDataSet,
    DataDocVariable,
    DataSetState,
)

from DatasetSchema import DatasetSchema


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

        self.dataset_metadata: DataDocDataSet
        self.variables_metadata: Dict[str, DataDocVariable] = {}

        self.read_metadata_document()

    def get_dataset_state(
        self, dataset_path: pathlib.Path = None
    ) -> Optional[DataSetState]:
        """Use the path to attempt to guess the state of the dataset"""

        if dataset_path is None:
            dataset_path = self.dataset_full_path
        dataset_path = list(dataset_path.parts)
        if "kildedata" in dataset_path:
            return DataSetState.SOURCE_DATA
        elif "inndata" in dataset_path:
            return DataSetState.INPUT_DATA
        elif "klargjorte_data" in dataset_path:
            return DataSetState.PROCESSED_DATA
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

            self.variables_metadata = {
                v[VariableIdentifiers.SHORT_NAME.value]: DataDocVariable(**v)
                for v in variables_list
            }
            self.dataset_metadata = DataDocDataSet(**fresh_metadata)
        else:
            self.generate_new_metadata_document()

    def generate_new_metadata_document(self):
        self.ds_schema = DatasetSchema(self.dataset)

        self.dataset_metadata = DataDocDataSet(
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

        self.variables_metadata = {v.short_name: v for v in self.ds_schema.get_fields()}

    def write_metadata_document(self) -> None:
        """Write all currently known metadata to file"""
        export_dict = self.dataset_metadata.dict()
        export_dict["variables"] = [v.dict() for v in self.variables_metadata.values()]
        json_str = json.dumps(export_dict, indent=4, sort_keys=False, default=str)
        self.metadata_document_full_path.write_text(json_str, encoding="utf-8")
