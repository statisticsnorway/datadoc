"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum

from datadoc_model import model
from datadoc_model.model import LanguageStringType


class DaplaRegion(str, Enum):
    """Dapla platforms/regions."""

    DAPLA_LAB = "DAPLA_LAB"
    BIP = "BIP"
    ON_PREM = "ON_PREM"
    CLOUD_RUN = "CLOUD_RUN"


class DaplaService(str, Enum):
    """Dapla services."""

    DATADOC = "DATADOC"
    JUPYTERLAB = "JUPYTERLAB"
    VS_CODE = "VS_CODE"
    R_STUDIO = "R_STUDIO"
    KILDOMATEN = "KILDOMATEN"


class SupportedLanguages(str, Enum):
    """The list of languages metadata may be recorded in.

    Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
    """

    NORSK_BOKMÅL = "nb"
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"


class LanguageStringsEnum(Enum):
    """Enum class for storing LanguageStringType objects."""

    def __init__(
        self,
        language_strings: LanguageStringType,
    ) -> None:
        """Store the LanguageStringType object for displaying enum values in multiple languages.

        We don't particularly care what the value of the enum is,
        but when serialised it's convenient and readable to use the
        name of the enum, so we set the value to be the name.
        """
        self._value_ = self.name
        self.language_strings = language_strings

    @classmethod
    def _missing_(cls, value: object) -> LanguageStringsEnum:
        """Support constructing an enum member from a supplied name string."""
        try:
            member: LanguageStringsEnum = cls._member_map_[str(value)]  # type: ignore [assignment]
        except KeyError as e:
            # Raise the expected exception with a useful explanation
            message = f"{value} is not a valid {cls.__qualname__}"
            raise ValueError(message) from e
        else:
            return member

    def get_value_for_language(
        self,
        language: SupportedLanguages,
    ) -> str:
        """Retrieve the string for the relevant language."""
        return str(getattr(self.language_strings, language.value))


class Assessment(LanguageStringsEnum):
    """Sensitivity of data."""

    SENSITIVE = LanguageStringType(
        en=model.Assessment.SENSITIVE.value,
        nn="SENSITIV",
        nb="SENSITIV",
    )
    PROTECTED = LanguageStringType(
        en=model.Assessment.PROTECTED.value,
        nn="SKJERMET",
        nb="SKJERMET",
    )
    OPEN = LanguageStringType(en=model.Assessment.OPEN.value, nn="ÅPEN", nb="ÅPEN")


class DataSetStatus(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DRAFT = LanguageStringType(
        en=model.DataSetStatus.DRAFT.value,
        nn="UTKAST",
        nb="UTKAST",
    )
    INTERNAL = LanguageStringType(
        en=model.DataSetStatus.INTERNAL.value,
        nn="INTERN",
        nb="INTERN",
    )
    EXTERNAL = LanguageStringType(
        en=model.DataSetStatus.EXTERNAL.value,
        nn="EKSTERN",
        nb="EKSTERN",
    )
    DEPRECATED = LanguageStringType(
        en=model.DataSetStatus.DEPRECATED.value,
        nn="UTGÅTT",
        nb="UTGÅTT",
    )


class DataSetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = LanguageStringType(
        en=model.DataSetState.SOURCE_DATA.value,
        nn="KILDEDATA",
        nb="KILDEDATA",
    )
    INPUT_DATA = LanguageStringType(
        en=model.DataSetState.INPUT_DATA.value,
        nn="INNDATA",
        nb="INNDATA",
    )
    PROCESSED_DATA = LanguageStringType(
        en=model.DataSetState.PROCESSED_DATA.value,
        nn="KLARGJORTE DATA",
        nb="KLARGJORTE DATA",
    )
    STATISTICS = LanguageStringType(
        en=model.DataSetState.STATISTICS.value,
        nn="STATISTIKK",
        nb="STATISTIKK",
    )
    OUTPUT_DATA = LanguageStringType(
        en=model.DataSetState.OUTPUT_DATA.value,
        nn="UTDATA",
        nb="UTDATA",
    )


class TemporalityTypeType(LanguageStringsEnum):
    """Temporality of a dataset.

    More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    """

    FIXED = LanguageStringType(
        en=model.TemporalityTypeType.FIXED.value,
        nn="FAST",
        nb="FAST",
    )
    STATUS = LanguageStringType(
        en=model.TemporalityTypeType.STATUS.value,
        nn="TVERRSNITT",
        nb="TVERRSNITT",
    )
    ACCUMULATED = LanguageStringType(
        en=model.TemporalityTypeType.ACCUMULATED.value,
        nn="AKKUMULERT",
        nb="AKKUMULERT",
    )
    EVENT = LanguageStringType(
        en=model.TemporalityTypeType.EVENT.value,
        nn="HENDELSE",
        nb="HENDELSE",
    )


class DataType(LanguageStringsEnum):
    """Simplified data types for metadata purposes."""

    STRING = LanguageStringType(en=model.DataType.STRING.value, nn="TEKST", nb="TEKST")
    INTEGER = LanguageStringType(
        en=model.DataType.INTEGER.value,
        nn="HELTALL",
        nb="HELTALL",
    )
    FLOAT = LanguageStringType(
        en=model.DataType.FLOAT.value,
        nn="DESIMALTALL",
        nb="DESIMALTALL",
    )
    DATETIME = LanguageStringType(
        en=model.DataType.DATETIME.value,
        nn="DATOTID",
        nb="DATOTID",
    )
    BOOLEAN = LanguageStringType(
        en=model.DataType.BOOLEAN.value,
        nn="BOOLSK",
        nb="BOOLSK",
    )


class VariableRole(LanguageStringsEnum):
    """The role of a variable in a dataset."""

    IDENTIFIER = LanguageStringType(
        en=model.VariableRole.IDENTIFIER.value,
        nn="IDENTIFIKATOR",
        nb="IDENTIFIKATOR",
    )
    MEASURE = LanguageStringType(
        en=model.VariableRole.MEASURE.value,
        nn="MÅLEVARIABEL",
        nb="MÅLEVARIABEL",
    )
    START_TIME = LanguageStringType(
        en=model.VariableRole.START_TIME.value,
        nn="STARTTID",
        nb="STARTTID",
    )
    STOP_TIME = LanguageStringType(
        en=model.VariableRole.STOP_TIME.value,
        nn="STOPPTID",
        nb="STOPPTID",
    )
    ATTRIBUTE = LanguageStringType(
        en=model.VariableRole.ATTRIBUTE.value,
        nn="ATTRIBUTT",
        nb="ATTRIBUTT",
    )
