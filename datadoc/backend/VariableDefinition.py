from xml.dom.minidom import parseString

import requests


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
