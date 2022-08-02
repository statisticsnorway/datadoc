from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, constr, conint

from datadoc_model import Enums

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


class MetadataDocument(DataDocBaseModel):
    """Represents the data structure on file. Includes the dataset metadata from the user as
    well as meta-metadata like the percentage of completed metadata fields and the document version"""

    percentage_complete: conint(ge=0, le=100)
    document_version: str = MODEL_VERSION
    dataset: DataDocDataSet
    variables: List[DataDocVariable]
