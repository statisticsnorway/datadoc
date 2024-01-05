"""Enumerations used in Datadoc."""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from datadoc_model.model import LanguageStringType

if TYPE_CHECKING:
    # Avoid circular imports
    from typing import Self


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
        self: Self @ LanguageStringsEnum,
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
    def _missing_(cls: type[Self @ LanguageStringsEnum], value: str) -> Enum:
        """Support constructing an enum member from a supplied name string."""
        try:
            member = cls._member_map_[value]
        except KeyError as e:
            # Raise the expected exception with a useful explanation
            message = f"{value} is not a valid {cls.__qualname__}"
            raise ValueError(message) from e
        else:
            return member

    def get_value_for_language(
        self: Self @ LanguageStringsEnum,
        language: SupportedLanguages,
    ) -> str:
        """Retrieve the string for the relevant language."""
        return getattr(self.language_strings, language.value)


class Assessment(LanguageStringsEnum):
    """Sensitivity of data."""

    SENSITIVE = LanguageStringType(en="SENSITIVE", nn="SENSITIV", nb="SENSITIV")
    PROTECTED = LanguageStringType(en="PROTECTED", nn="BESKYTTET", nb="BESKYTTET")
    OPEN = LanguageStringType(en="OPEN", nn="ÅPEN", nb="ÅPEN")


class DatasetStatus(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DRAFT = LanguageStringType(en="DRAFT", nn="UTKAST", nb="UTKAST")
    INTERNAL = LanguageStringType(en="INTERNAL", nn="INTERN", nb="INTERN")
    EXTERNAL = LanguageStringType(en="EXTERNAL", nn="EKSTERN", nb="EKSTERN")
    DEPRECATED = LanguageStringType(en="DEPRECATED", nn="UTGÅTT", nb="UTGÅTT")


class DatasetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = LanguageStringType(en="SOURCE DATA", nn="KILDEDATA", nb="KILDEDATA")
    INPUT_DATA = LanguageStringType(en="INPUT DATA", nn="INNDATA", nb="INNDATA")
    PROCESSED_DATA = LanguageStringType(
        en="PROCESSED DATA",
        nn="KLARGJORTE DATA",
        nb="KLARGJORTE DATA",
    )
    STATISTICS = LanguageStringType(en="STATISTICS", nn="STATISTIKK", nb="STATISTIKK")
    OUTPUT_DATA = LanguageStringType(en="OUTPUT DATA", nn="UTDATA", nb="UTDATA")


class UnitType(LanguageStringsEnum):
    """Statistical unit types.

    Ref: https://www.ssb.no/metadata/definisjoner-av-statistiske-enheter.
    """

    ARBEIDSULYKKE = LanguageStringType(
        en="WORK ACCIDENT",
        nn="ARBEIDSULYKKE",
        nb="ARBEIDSULYKKE",
    )
    BOLIG = LanguageStringType(en="HOUSING", nn="BOLIG", nb="BOLIG")
    BYGNING = LanguageStringType(en="BUILDING", nn="BYGNING", nb="BYGNING")
    EIENDOM = LanguageStringType(en="PROPERTY", nn="EIENDOM", nb="EIENDOM")
    FAMILIE = LanguageStringType(en="FAMILY", nn="FAMILIE", nb="FAMILIE")
    FORETAK = LanguageStringType(en="COMPANY", nn="FORETAK", nb="FORETAK")
    FYLKE = LanguageStringType(en="REGION", nn="FYLKE", nb="FYLKE")
    HAVNEANLOEP = LanguageStringType(en="PORT CALL", nn="HAVNEANLOEP", nb="HAVNEANLOEP")
    HUSHOLDNING = LanguageStringType(en="HOUSEHOLD", nn="HUSHOLDNING", nb="HUSHOLDNING")
    KJOERETOEY = LanguageStringType(en="VEHICLE", nn="KJOERETOEY", nb="KJOERETOEY")
    KOMMUNE = LanguageStringType(en="COUNTY", nn="KOMMUNE", nb="KOMMUNE")
    KURS = LanguageStringType(en="COURSE", nn="KURS", nb="KURS")
    LOVBRUDD = LanguageStringType(en="CRIME", nn="LOVBRUDD", nb="LOVBRUDD")
    PERSON = LanguageStringType(en="PERSON", nn="PERSON", nb="PERSON")
    STAT = LanguageStringType(en="STATE", nn="STAT", nb="STAT")
    STORFE = LanguageStringType(en="CATTLE", nn="STORFE", nb="STORFE")
    TRAFIKKULYKKE = LanguageStringType(
        en="TRAFFIC ACCIDENT",
        nn="TRAFIKKULYKKE",
        nb="TRAFIKKULYKKE",
    )
    TRANSAKSJON = LanguageStringType(
        en="TRANSACTION",
        nn="TRANSAKSJON",
        nb="TRANSAKSJON",
    )
    VARE_TJENESTE = LanguageStringType(
        en="GOOD/SERVICE",
        nn="VARE/TJENESTE",
        nb="VARE/TJENESTE",
    )
    VERDIPAPIR = LanguageStringType(en="SERVICE", nn="VERDIPAPIR", nb="VERDIPAPIR")
    VIRKSOMHET = LanguageStringType(en="BUSINESS", nn="VIRKSOMHET", nb="VIRKSOMHET")


class TemporalityTypeType(LanguageStringsEnum):
    """Temporality of a dataset.

    More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    """

    FIXED = LanguageStringType(en="FIXED", nn="FAST", nb="FAST")
    STATUS = LanguageStringType(en="STATUS", nn="TVERRSNITT", nb="TVERRSNITT")
    ACCUMULATED = LanguageStringType(en="ACCUMULATED", nn="AKKUMULERT", nb="AKKUMULERT")
    EVENT = LanguageStringType(en="EVENT", nn="HENDELSE", nb="HENDELSE")


class DataType(LanguageStringsEnum):
    """Simplified data types for metadata purposes."""

    STRING = LanguageStringType(en="STRING", nn="TEKST", nb="TEKST")
    INTEGER = LanguageStringType(en="INTEGER", nn="HELTALL", nb="HELTALL")
    FLOAT = LanguageStringType(en="FLOAT", nn="DESIMALTALL", nb="DESIMALTALL")
    DATETIME = LanguageStringType(en="DATETIME", nn="DATOTID", nb="DATOTID")
    BOOLEAN = LanguageStringType(en="BOOLEAN", nn="BOOLSK", nb="BOOLSK")


class VariableRole(LanguageStringsEnum):
    """The role of a variable in a dataset."""

    IDENTIFIER = LanguageStringType(
        en="IDENTIFIER",
        nn="IDENTIFIKATOR",
        nb="IDENTIFIKATOR",
    )
    MEASURE = LanguageStringType(en="MEASURE", nn="MÅLEVARIABEL", nb="MÅLEVARIABEL")
    START_TIME = LanguageStringType(en="START_TIME", nn="STARTTID", nb="STARTTID")
    STOP_TIME = LanguageStringType(en="STOP_TIME", nn="STOPPTID", nb="STOPPTID")
    ATTRIBUTE = LanguageStringType(en="ATTRIBUTE", nn="ATTRIBUTT", nb="ATTRIBUTT")
