import json
import pathlib
import datetime
import os

from .DatasetSchema import DatasetSchema


class DataDocMetadata:
    def __init__(self, dataset):
        # TODO: Denne delen må tilpasses lesing av datasett fra Google buckets også
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
            self.current_user = "default_user"
        self.current_datetime = str(datetime.datetime.now())
        self.meta = {}
        self.read_metadata_document()

    def get_dataset_state(self, dataset_path: pathlib.Path = None):
        """Use the path to attempt to guess the state of the dataset"""

        if dataset_path is None:
            dataset_path = self.dataset_full_path
        dataset_path = list(dataset_path.parts)
        if "kildedata" in dataset_path:
            return "SOURCE_DATA"
        elif "inndata" in dataset_path:
            return "INPUT_DATA"
        elif "klargjorte_data" in dataset_path:
            return "PROCESSED_DATA"
        else:
            return None

    def get_dataset_version(self):
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
        if self.metadata_document_full_path.exists():
            with open(self.metadata_document_full_path, "r", encoding="utf-8") as JSON:
                self.meta = json.load(JSON)
            print(
                "Opened existing metadata file " + str(self.metadata_document_full_path)
            )
        else:
            self.generate_new_metadata_document()

    def generate_new_metadata_document(self):
        self.ds_schema = DatasetSchema(self.dataset)
        self.ds_fields = self.ds_schema.get_fields()

        # Dataset elements
        self.meta["dataSourcePath"] = str(self.dataset_full_path)
        self.meta["shortName"] = str(self.dataset_stem)
        self.meta["name"] = []
        self.meta["dataSetState"] = self.dataset_state
        self.meta["description"] = []
        self.meta["temporalityType"] = None
        self.meta["spatialCoverageDescription"] = [
            {"languageCode": "no", "value": "Norge"}
        ]
        self.meta["populationDescription"] = []
        self.meta["id"] = None
        self.meta["createdDate"] = self.current_datetime
        self.meta["createdBy"] = self.current_user
        self.meta["dataOwner"] = None
        self.meta["lastUpdatedDate"] = None
        self.meta["lastUpdatedBy"] = None
        self.meta["version"] = self.dataset_version
        self.meta["administrativeStatus"] = "DRAFT"

        # Elements for instance variables (dataset fields)
        self.meta["variables"] = []
        for field in self.ds_fields:
            variable = {}
            variable["shortName"] = field["shortName"]
            try:
                variable["name"] = field["name"]
            except KeyError:
                variable["name"] = None
            variable["dataType"] = field["dataType"]
            variable["variableRole"] = None
            # Eksempel VarDok XML, Sivilstand:
            # https://www.ssb.no/a/xml/metadata/conceptvariable/vardok/91/nb
            variable["definitionUri"] = None
            variable["populationDescription"] = None  # TODO: Støtte flere språk!
            variable["comment"] = None  # TODO: Støtte flere språk!
            variable["temporalityType"] = None
            variable["mesurementType"] = None
            variable["measurementUnit"] = None
            variable["format"] = None
            variable["sentinelAndMissingValueUri"] = []
            variable["unitType"] = None
            variable["foreignKeyType"] = None
            self.meta["variables"].append(variable)
        # print(self.meta)

    def write_metadata_document(self):
        json_str = json.dumps(self.meta, indent=4, sort_keys=False)
        self.metadata_document_full_path.write_text(json_str, encoding="utf-8")
