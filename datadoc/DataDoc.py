import datetime
import json
import os
import pathlib
from xml.dom.minidom import parseString

import ipysheet
import requests
from ipysheet import sheet
from IPython.display import display
from ipywidgets import Layout, widgets

from .DataDocMetadata import DataDocMetadata

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
