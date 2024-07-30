"""Repository for constant values in Datadoc backend."""

from datadoc.enums import LanguageStringType
from datadoc.enums import LanguageStringTypeItem

VALIDATION_ERROR = "Validation error: "

DATE_VALIDATION_MESSAGE = f"{VALIDATION_ERROR}contains_data_from must be the same or earlier date than contains_data_until"

OBLIGATORY_METADATA_WARNING = "Obligatory metadata is missing: "

INCONSISTENCIES_MESSAGE = "Inconsistencies found between extracted and existing metadata. Inconsistencies are:"

OBLIGATORY_DATASET_METADATA_IDENTIFIERS: list = [
    "assessment",
    "dataset_state",
    "dataset_status",
    "name",
    "description",
    "data_source",
    "population_description",
    "version",
    "version_description",
    "unit_type",
    "temporality_type",
    "subject_field",
    "spatial_coverage_description",
    "owner",
    "contains_data_from",
    "contains_data_until",
    "contains_personal_data",
]

OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE = [
    "name",
    "description",
    "population_description",
    "version_description",
    "spatial_coverage_description",
]

OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS = [
    "name",
    "data_type",
    "variable_role",
    "is_personal_data",
]

OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE = [
    "name",
]

DEFAULT_SPATIAL_COVERAGE_DESCRIPTION = LanguageStringType(
    [
        LanguageStringTypeItem(
            languageCode="nb",
            languageText="Norge",
        ),
        LanguageStringTypeItem(
            languageCode="nn",
            languageText="Noreg",
        ),
        LanguageStringTypeItem(
            languageCode="en",
            languageText="Norway",
        ),
    ],
)

NUM_OBLIGATORY_DATASET_FIELDS = len(OBLIGATORY_DATASET_METADATA_IDENTIFIERS)

NUM_OBLIGATORY_VARIABLES_FIELDS = len(OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS)

DATASET_FIELDS_FROM_EXISTING_METADATA = [
    "dataset_status",
    "name",
    "description",
    "data_source",
    "population_description",
    "unit_type",
    "temporality_type",
    "subject_field",
    "keyword",
    "spatial_coverage_description",
    "contains_personal_data",
    "use_restriction",
    "use_restriction_date",
    "custom_type",
    "owner",
]
