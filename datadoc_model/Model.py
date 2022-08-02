from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, constr, conint

from datadoc_model import Enums
from datadoc import state
from datadoc.utils import calculate_percentage
import datadoc.frontend.DisplayDataset as DisplayDataset
import datadoc.frontend.DisplayVariables as DisplayVariables

MODEL_VERSION = "0.1.0"

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"
URL_FORMAT = "(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([-a-zA-Z0-9.]{1,254}[A-Za-z0-9])?\.[a-zA-Z0-9()]{1,6}([\/][-a-zA-Z0-9_]+)*[\/]?"  # noqa: W605


class DataDocBaseModel(BaseModel):
    """Defines configuration which applies to all Models in this application"""

    class Config:
        # Runs validation when a field value is assigned, not just in the constructor
        validate_assignment = True
        # Write only the values of enums during serialization
        use_enum_values = True


class LanguageStrings(DataDocBaseModel):
    en: str = ""
    nn: str = ""
    nb: str = ""

    def get_string_for_current_language(self):
        return self.dict()[state.current_metadata_language.value]


class DataDocDataSet(DataDocBaseModel):
    """DataDoc data set. See documentation https://statistics-norway.atlassian.net/l/c/NgjE7yj1"""

    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    assessment: Optional[Enums.Assessment]
    dataset_status: Optional[Enums.DatasetStatus] = Enums.DatasetStatus.DRAFT
    dataset_state: Optional[Enums.DatasetState]
    name: Optional[LanguageStrings]
    data_source: Optional[LanguageStrings]
    population_description: Optional[LanguageStrings]
    version: Optional[str]
    unit_type: Optional[Enums.UnitType]
    temporality_type: Optional[Enums.TemporalityType]
    description: Optional[LanguageStrings]
    subject_field: Optional[LanguageStrings]
    spatial_coverage_description: Optional[LanguageStrings]
    id: Optional[constr(regex=URL_FORMAT)]
    owner: Optional[LanguageStrings]
    data_source_path: Optional[str]
    created_date: Optional[datetime]
    created_by: Optional[str]
    last_updated_date: Optional[datetime]
    last_updated_by: Optional[str]


class DataDocVariable(DataDocBaseModel):
    """DataDoc instance variable. See documentation https://statistics-norway.atlassian.net/l/c/goyNhUPP"""

    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    name: Optional[LanguageStrings]
    data_type: Optional[Enums.Datatype]
    variable_role: Optional[Enums.VariableRole]
    definition_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    direct_person_identifying: Optional[bool]
    data_source: Optional[LanguageStrings]
    population_description: Optional[LanguageStrings]
    comment: Optional[LanguageStrings]
    temporality_type: Optional[Enums.TemporalityType]
    # TODO: measurement_unit implemented as string. In the future this should be implemente as a class? See https://www.ssb.no/klass/klassifikasjoner/303/koder
    measurement_unit: Optional[LanguageStrings]
    format: Optional[str]
    classification_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    sentinel_value_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    invalid_value_description: Optional[LanguageStrings]
    id: Optional[constr(regex=URL_FORMAT)]
    contains_data_from: Optional[date]
    contains_data_until: Optional[date]

    def get_display_values(self) -> dict:
        return_dict = {}
        for field_name, value in self:
            if isinstance(value, LanguageStrings):
                value = value.get_string_for_current_language()
            return_dict[field_name] = value
        return return_dict


OBLIGATORY_DATASET_METADATA = [
    m.identifier for m in DisplayDataset.DISPLAY_DATASET.values() if m.obligatory
]

OBLIGATORY_VARIABLES_METADATA = [
    m.identifier for m in DisplayVariables.DISPLAY_VARIABLES.values() if m.obligatory
]

# These don't vary at runtime so we calculate them as constants here
NUM_OBLIGATORY_DATASET_FIELDS = len(
    [k for k in DataDocDataSet().dict().keys() if k in OBLIGATORY_DATASET_METADATA]
)
NUM_OBLIGATORY_VARIABLES_FIELDS = len(
    [k for k in DataDocVariable().dict().keys() if k in OBLIGATORY_VARIABLES_METADATA]
)


class MetadataDocument(DataDocBaseModel):
    """Represents the data structure on file. Includes the dataset metadata from the user as
    well as meta-metadata like the percentage of completed metadata fields and the document version"""

    percentage_complete: conint(ge=0, le=100)
    document_version: str = MODEL_VERSION
    dataset: DataDocDataSet
    variables: List[DataDocVariable]

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
                for k, v in self.dataset.dict().items()
                if k in OBLIGATORY_DATASET_METADATA and v is not None
            ]
        )

        for variable in self.variables:
            num_all_fields += NUM_OBLIGATORY_VARIABLES_FIELDS
            num_set_fields += len(
                [
                    k
                    for k, v in variable.dict().items()
                    if k in OBLIGATORY_VARIABLES_METADATA and v is not None
                ]
            )

        return calculate_percentage(num_set_fields, num_all_fields)
