import datetime
import json
import os
import pathlib
from typing import Optional
from xml.dom.minidom import parseString

import ipysheet
import pyarrow.parquet as pq
import requests
from ipysheet import sheet
from IPython.display import display
from ipywidgets import Layout, widgets

# Example usage:
# --------------
# import data_doc as datadoc
# dd = datadoc.DataDocGui(dataset="./my_directory/my_dataset.parquet")


class DataDocGui:
    def __init__(self, dataset):
        self.dataset = dataset
        self.datadoc_meta = DataDocMetadata(self.dataset)
        self.meta = self.datadoc_meta.meta

        # Dataset GUI elements
        self.datadoc_header_text = widgets.HTML(
            value="""<h1 style='font-size:20px'>DataDoc -
            dokumentasjon av datasett og variabler</h1>"""
        )
        self.button_save = widgets.Button(
            description="Lagre", tooltip="Lagre datadokumentasjon til fil (JSON-fil)"
        )
        self.button_save.on_click(self.save_button_clicked)

        self.dropdown_language_code = widgets.Dropdown(
            options=[
                ("Norsk (no)", "no"),
                ("Norsk bokmål (nb)", "nb"),
                ("Nynorsk (nn)", "nn"),
                ("Engelsk (en)", "en"),
            ],
            value="no",
            description="Språk:",
        )
        self.datadoc_header_hbox = widgets.HBox(
            children=[self.button_save, self.dropdown_language_code],
            layout=Layout(border="1px solid grey"),
        )

        self.ds_header2 = widgets.HTML(value="<h1 style='font-size:16px'>Datasett</h1>")
        self.ds_short_name = widgets.Text(
            value=self.meta["shortName"],
            placeholder="Oppgi datasett kortnavn",
            description="Kortnavn:",
            disabled=False,
        )
        self.ds_name = widgets.Text(
            value=self.get_language_value("name", self.dropdown_language_code.value),
            placeholder="Oppgi datasett navn (tittel)",
            description="Navn:",
            disabled=False,
            layout={"height": "auto", "width": "50%"},
        )
        self.ds_description = widgets.Textarea(
            value=self.get_language_value(
                "description", self.dropdown_language_code.value
            ),
            placeholder="Oppgi datasett beskrivelse",
            description="Beskrivelse:",
            disabled=False,
            layout={"height": "auto", "width": "50%"},
        )
        self.ds_data_set_state = widgets.Dropdown(
            options=[
                ("Kildedata", "SOURCE_DATA"),
                ("Inndata", "INPUT_DATA"),
                ("Klargjorte data", "PROCESSED_DATA"),
            ],
            value=self.meta["dataSetState"],
            description="Datatilstand:",
        )
        self.ds_version = widgets.Text(
            value=self.meta["version"],
            placeholder="Oppgi versjon",
            description="Versjon:",
            disabled=False,
        )
        self.ds_data_source_path = widgets.Text(
            value=self.meta["dataSourcePath"],
            placeholder="filsti",
            description="Datasett sti:",
            disabled=True,
            layout=Layout(width="50%"),
        )
        self.ds_created_by = widgets.Text(
            value=self.meta["createdBy"],
            placeholder="initialer",
            description="Opprettet av:",
            disabled=True,
        )
        self.ds_created_date = widgets.Text(
            value=self.meta["createdDate"],
            placeholder="dato",
            description="Oppr. dato:",
            disabled=True,
        )

        self.ds_vbox_details = widgets.VBox(
            children=[
                self.ds_data_set_state,
                self.ds_version,
                self.ds_data_source_path,
                self.ds_created_by,
                self.ds_created_date,
            ]
        )
        # Link to VarDef
        self.vardef_link = widgets.HTML(
            value=(
                "<a style='font-size:16px;color:blue'"
                " href=https://www.ssb.no/a/metadata/definisjoner/variabler/main.html"
                " target='_blank'>Gå til VarDef (variabeldefinisjoner)</a>"
            )
        )

        # Varible GUI elements
        self.variable_sheet = ipysheet.sheet(
            key="variable_sheet",
            column_headers=[
                "Kortnavn",
                "Navn",
                "Datatype",
                "Variabelelens rolle i datasettet",
                "VarDef ID",
                "Kommentar",
            ],
            row_headers=False,
            rows=len(self.meta["variables"]),
            columns=6,  # TODO må justeres hvis flere kolonner skal inn
        )
        sheet("variable_sheet")  # Activate the wanted sheet with "sheet key"
        self.col_num_short_name = 0
        self.col_num_name = 1
        self.col_num_datatype = 2
        self.col_num_variable_role = 3
        self.col_num_definition_uri = 4
        self.col_num_comment = 5

        # Set initial values in each column for each variable
        for row_num, variable in enumerate(self.meta["variables"]):
            ipysheet.cell(
                row_num, self.col_num_short_name, value=str(variable["shortName"])
            )
            ipysheet.cell(row_num, self.col_num_name, value=variable["name"])
            ipysheet.cell(
                row_num,
                self.col_num_datatype,
                value=variable["dataType"],
                choice=["STRING", "INTEGER", "FLOAT", "DATETIME", "BOOLEAN"],
            )
            ipysheet.cell(
                row_num,
                self.col_num_variable_role,
                value=variable["variableRole"],
                choice=[
                    "IDENTIFIER",
                    "MEASURE",
                    "START_TIME",
                    "STOP_TIME",
                    "ATTRIBUTE",
                ],
            )
            ipysheet.cell(row_num, self.col_num_comment, value=variable["comment"])
            tmp_definition_uri = ipysheet.cell(
                row_num, self.col_num_definition_uri, value=variable["definitionUri"]
            )
            tmp_definition_uri.observe(self.cell_definition_uri_changed, "value")

        self.ds_accordion = widgets.Accordion(
            children=[self.variable_sheet], layout=Layout(display="flex")
        )
        self.ds_accordion.set_title(0, "Variabler som inngår i datasettet")
        self.ds_accordion.selected_index = 0

        self.ds_accordion2 = widgets.Accordion(children=[self.ds_vbox_details])
        self.ds_accordion2.set_title(0, "Datasett detaljer")
        # Dispaly GUI
        self.setup_gui_dataset_elements()

    def get_language_value(self, language_element, language_code):
        # print(self.meta[language_element])
        if language_element in self.meta:
            for language in self.meta[language_element]:
                if language["languageCode"] == language_code:
                    return language["value"]
        return ""  # Element or language not found

    def create_or_update_language_value(
        self, language_element, language_code, language_value
    ):
        if language_element in self.meta:
            for language in self.meta[language_element]:
                if language["languageCode"] == language_code:
                    # Update existing
                    language.update({"value": language_value})
                    return
        # Not found, create new
        self.meta[language_element].append(
            {"languageCode": language_code, "value": language_value}
        )

    def update_dataset_metadata_from_gui_elements(self):
        # self.meta['name'].append({'languageCode': 'no', 'value': self.ds_name.value})
        self.create_or_update_language_value(
            "name", self.dropdown_language_code.value, self.ds_name.value
        )
        self.create_or_update_language_value(
            "description", self.dropdown_language_code.value, self.ds_description.value
        )
        self.update_variable_metadata_from_gui_elements()

    def update_variable_metadata_from_gui_elements(self):
        # print(self.variable_sheet.cells)
        self.meta["variables"] = []
        variable = {}
        for cell_item in self.variable_sheet.cells:
            if cell_item.column_start == 0:
                variable["shortName"] = cell_item.value
            elif cell_item.column_start == 1:
                variable["name"] = cell_item.value  # TODO: Støtte flere språk!
            elif cell_item.column_start == 2:
                variable["dataType"] = cell_item.value
            elif cell_item.column_start == 3:
                variable["variableRole"] = cell_item.value
            elif cell_item.column_start == 4:
                variable["definitionUri"] = cell_item.value
            elif cell_item.column_start == 5:
                variable["comment"] = cell_item.value  # TODO: Støtte flere språk!
                # TODO: Mappe disse mot variabel-sheet i GUI også!!!
                variable["populationDescription"] = None  # TODO: Støtte flere språk!
                variable["temporalityType"] = None
                variable["mesurementType"] = None
                variable["measurementUnit"] = None
                variable["format"] = None
                variable["sentinelAndMissingValueUri"] = []
                variable["unitType"] = None
                variable["foreignKeyType"] = None
                self.meta["variables"].append(variable)  # Legger til ny variabel
                variable = {}  # Nullstiller før neste runde i loopen

    def save_button_clicked(self, b):
        self.update_dataset_metadata_from_gui_elements()
        self.datadoc_meta.write_metadata_document()
        print(
            "DataDoc metadata saved to file "
            + str(self.datadoc_meta.metadata_document_full_path)
        )

    def setup_gui_dataset_elements(self):
        # Må settes for at widget skal vises i notebook
        display(
            self.datadoc_header_text,
            self.datadoc_header_hbox,
            self.ds_header2,
            self.ds_short_name,
            self.ds_name,
            self.ds_description,
            self.ds_accordion2,
            self.ds_accordion,
            self.vardef_link,
        )

    def cell_definition_uri_changed(self, change):
        # For more information aout observe and events:
        # https://ipysheet.readthedocs.io/en/stable/index.html?highlight=observe#Events
        try:
            vardef_id = change["new"]
            cell_changed = change["owner"]
            row_num = cell_changed.row_start

            vardef = VariableDefinition(vardef_id)
            # TODO: støtte flere språk!
            ipysheet.cell(row_num, self.col_num_name, value=vardef.vardef_name)
            ipysheet.cell(row_num, self.col_num_comment, vardef.vardef_definition)
        except requests.RequestException:
            print('Fant ikke variabeldefinisjon med VarDef-ID "' + vardef_id + '"')


class DatasetSchema:
    def __init__(self, dataset):
        self.dataset = dataset
        self.dataset_full_path = pathlib.Path(self.dataset)
        self.dataset_file_type = str(self.dataset_full_path.name).lower().split(".")[1]

    def get_fields(self):
        fields = []
        if self.dataset_file_type == "parquet":
            data_table = pq.read_table(self.dataset)
            for data_field in data_table.schema:
                field = {}
                field["name"] = str(data_field.name)
                field["datatype"] = self.transform_datatype(str(data_field.type))
                fields.append(field)
        elif self.dataset_file_type == "csv":
            raise NotImplementedError
        elif self.dataset_file_type == "json":
            raise NotImplementedError
        elif self.dataset_file_type == "xml":
            raise NotImplementedError
        return fields

    @staticmethod
    def transform_datatype(data_type) -> Optional[str]:
        v_data_type = data_type.lower()
        if v_data_type in (
            "int",
            "int_",
            "int8",
            "int16",
            "int32",
            "int64",
            "integer",
            "long",
            "uint",
            "uint8",
            "uint16",
            "uint32",
            "uint64",
        ):
            return "INTEGER"
        elif v_data_type in (
            "double",
            "float",
            "float_",
            "float16",
            "float32",
            "float64",
            "decimal",
            "number",
            "numeric",
            "num",
        ):
            return "FLOAT"
        elif v_data_type in (
            "string",
            "str",
            "char",
            "varchar",
            "varchar2",
            "text",
            "txt",
        ):
            return "STRING"
        elif v_data_type in (
            "timestamp",
            "timestamp[us]",
            "timestamp[ns]",
            "datetime64",
            " datetime64[ns]",
            " datetime64[us]",
            "date",
            "datetime",
            "time",
        ):
            return "DATETIME"
        elif v_data_type in ("bool", "bool_", "boolean"):
            return "BOOLEAN"
        else:
            return None  # Unknown datatype?


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
        self.dataset_state = self.get_dataset_state()
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

    def get_dataset_state(self):
        for directory_element in pathlib.PurePath(self.dataset_full_path).parts:
            dir_element = str(directory_element).lower()
            # print(dir_element)
            if dir_element == "kildedata":
                return "SOURCE_DATA"
            elif dir_element == "inndata":
                return "INPUT_DATA"
            elif dir_element == "klargjorte_data":
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
            variable["shortName"] = field["name"]
            variable["name"] = None  # TODO: Støtte flere språk!
            variable["dataType"] = field["datatype"]
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


class VariableDefinition:
    # TODO: Denne skal gå mot ny VarDef, men bruker foreløpig gamle VarDok!
    def __init__(self, vardef_id):
        self.vardef_id = vardef_id
        self.vardef_uri = (
            "https://www.ssb.no/a/xml/metadata/conceptvariable/vardok/"
            + self.vardef_id
            + "/nb"
        )
        self.vardef_gui_uri = (
            "https://www.ssb.no/a/metadata/conceptvariable/vardok/"
            + self.vardef_id
            + "/nb"
        )
        self.vardef_name = None
        self.vardef_definition = None
        self.vardef_short_name = None
        self.get_variable_definition()

    def get_variable_definition(self):
        # TODO: Denne skal gå mot ny VarDef, men bruker foreløpig gamle VarDok!
        vardok_xml = requests.get(self.vardef_uri)
        variable_document = parseString(vardok_xml.text)
        self.vardef_name = variable_document.getElementsByTagName("Title")[
            0
        ].firstChild.nodeValue
        self.vardef_definition = variable_document.getElementsByTagName("Description")[
            0
        ].firstChild.nodeValue


if __name__ == "__main__":
    DataDocGui("./klargjorte_data/person_data_v1.parquet")
