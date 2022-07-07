from enum import Enum, auto
from datetime import date, datetime
import statistics
from typing import Dict, List, Optional
from pydantic import BaseModel, constr, conint, Field

from datadoc.DisplayDataset import OBLIGATORY_DATASET_METADATA
from datadoc import Enums
from datadoc.DisplayVariables import OBLIGATORY_VARIABLES_METADATA

ALPHANUMERIC_HYPHEN_UNDERSCORE = "[-A-Za-z0-9_.*/]"
URL_FORMAT = "(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([-a-zA-Z0-9.]{1,254}[A-Za-z0-9])?\.[a-zA-Z0-9()]{1,6}([\/][-a-zA-Z0-9_]+)*[\/]?"


def calculate_percentage(num_set_fields: int, num_all_fields: int) -> int:
    return round((num_set_fields / num_all_fields) * 100)


class DataDocBaseModel(BaseModel):
    """Defines configuration which applies to all Models in this application"""

    class Config:
        # Runs validation when a field value is assigned, not just in the constructor
        validate_assignment = True
        # Write only the values of enums during serialization
        use_enum_values = True


class DataDocDataSet(DataDocBaseModel):
    """DataDoc data set. See documentation https://statistics-norway.atlassian.net/l/c/NgjE7yj1"""

    short_name: Optional[
        constr(min_length=1, max_length=63, regex=ALPHANUMERIC_HYPHEN_UNDERSCORE)
    ]
    assessment: Optional[Enums.Assessment]
    dataset_state: Optional[Enums.DatasetState]
    name: Optional[str]
    data_source: Optional[str]
    population_description: Optional[str]
    dataset_status: Optional[Enums.DatasetStatus] = Enums.DatasetStatus.DRAFT
    version: Optional[str]
    unit_type: Optional[Enums.UnitType]
    temporality_type: Optional[Enums.TemporalityType]
    description: Optional[str]
    spatial_coverage_description: Optional[List[Dict[str, str]]]
    id: Optional[constr(regex=URL_FORMAT)]
    owner: Optional[str]
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
    name: Optional[str]
    datatype: Optional[Enums.Datatype]
    variable_role: Optional[Enums.VariableRole]
    definition_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    direct_person_identifying: Optional[bool]
    data_source: Optional[str]
    population_description: Optional[str]
    comment: Optional[str]
    temporality_type: Optional[Enums.TemporalityType]
    # TODO: measurement_unit implemented as string. In the future this should be implemente as a class? See https://www.ssb.no/klass/klassifikasjoner/303/koder
    measurement_unit: Optional[str]
    format: Optional[str]
    classification_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    sentinel_value_uri: Optional[constr(min_length=1, max_length=63, regex=URL_FORMAT)]
    invalid_value_description: Optional[str]
    id: Optional[constr(regex=URL_FORMAT)]
    contains_data_from: Optional[date]
    contains_data_until: Optional[date]


class MetadataDocument(DataDocBaseModel):
    """Represents the data structure on file. Includes the dataset metadata from the user as
    well as meta-metadata like the percentage of completed metadata fields and the document version"""

    percentage_complete: conint(ge=0, le=100)
    document_version: str
    dataset: DataDocDataSet
    variables: List[DataDocVariable]

    @property
    def percent_complete(self) -> int:
        num_all_fields = len(
            [f for f in self.dataset.__fields__ if f in OBLIGATORY_DATASET_METADATA]
        )
        num_set_fields = len(
            [f for f in self.dataset.__fields_set__ if f in OBLIGATORY_DATASET_METADATA]
        )

        for v in self.variables:
            num_all_fields += len(
                [f for f in v.__fields__ if f in OBLIGATORY_VARIABLES_METADATA]
            )
            num_set_fields += len(
                [f for f in v.__fields_set__ if f in OBLIGATORY_VARIABLES_METADATA]
            )

        return calculate_percentage(num_set_fields, num_all_fields)
