"""Enumerations used in Datadoc."""
from __future__ import annotations

from enum import Enum

from datadoc_model import model
from datadoc_model.model import LanguageStringType


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
        nn="BESKYTTET",
        nb="BESKYTTET",
    )
    OPEN = LanguageStringType(en=model.Assessment.OPEN.value, nn="ÅPEN", nb="ÅPEN")


class DatasetStatus(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DRAFT = LanguageStringType(
        en=model.DatasetStatus.DRAFT.value,
        nn="UTKAST",
        nb="UTKAST",
    )
    INTERNAL = LanguageStringType(
        en=model.DatasetStatus.INTERNAL.value,
        nn="INTERN",
        nb="INTERN",
    )
    EXTERNAL = LanguageStringType(
        en=model.DatasetStatus.EXTERNAL.value,
        nn="EKSTERN",
        nb="EKSTERN",
    )
    DEPRECATED = LanguageStringType(
        en=model.DatasetStatus.DEPRECATED.value,
        nn="UTGÅTT",
        nb="UTGÅTT",
    )


class DatasetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = LanguageStringType(
        en=model.DatasetState.SOURCE_DATA.value,
        nn="KILDEDATA",
        nb="KILDEDATA",
    )
    INPUT_DATA = LanguageStringType(
        en=model.DatasetState.INPUT_DATA.value,
        nn="INNDATA",
        nb="INNDATA",
    )
    PROCESSED_DATA = LanguageStringType(
        en=model.DatasetState.PROCESSED_DATA.value,
        nn="KLARGJORTE DATA",
        nb="KLARGJORTE DATA",
    )
    STATISTICS = LanguageStringType(
        en=model.DatasetState.STATISTICS.value,
        nn="STATISTIKK",
        nb="STATISTIKK",
    )
    OUTPUT_DATA = LanguageStringType(
        en=model.DatasetState.OUTPUT_DATA.value,
        nn="UTDATA",
        nb="UTDATA",
    )


class UnitType(LanguageStringsEnum):
    """Statistical unit types.

    Ref: https://www.ssb.no/metadata/definisjoner-av-statistiske-enheter.
    """

    ARBEIDSULYKKE = LanguageStringType(
        en="WORK ACCIDENT",
        nn=model.UnitType.ARBEIDSULYKKE.value,
        nb=model.UnitType.ARBEIDSULYKKE.value,
    )
    BOLIG = LanguageStringType(
        en="HOUSING",
        nn=model.UnitType.BOLIG.value,
        nb=model.UnitType.BOLIG.value,
    )
    BYGNING = LanguageStringType(
        en="BUILDING",
        nn=model.UnitType.BYGNING.value,
        nb=model.UnitType.BYGNING.value,
    )
    EIENDOM = LanguageStringType(
        en="PROPERTY",
        nn=model.UnitType.EIENDOM.value,
        nb=model.UnitType.EIENDOM.value,
    )
    FAMILIE = LanguageStringType(
        en="FAMILY",
        nn=model.UnitType.FAMILIE.value,
        nb=model.UnitType.FAMILIE.value,
    )
    FORETAK = LanguageStringType(
        en="COMPANY",
        nn=model.UnitType.FORETAK.value,
        nb=model.UnitType.FORETAK.value,
    )
    FYLKE = LanguageStringType(
        en="REGION",
        nn=model.UnitType.FYLKE.value,
        nb=model.UnitType.FYLKE.value,
    )
    HAVNEANLOEP = LanguageStringType(
        en="PORT CALL",
        nn=model.UnitType.HAVNEANLOEP.value,
        nb=model.UnitType.HAVNEANLOEP.value,
    )
    HUSHOLDNING = LanguageStringType(
        en="HOUSEHOLD",
        nn=model.UnitType.HUSHOLDNING.value,
        nb=model.UnitType.HUSHOLDNING.value,
    )
    KJOERETOEY = LanguageStringType(
        en="VEHICLE",
        nn=model.UnitType.KJOERETOEY.value,
        nb=model.UnitType.KJOERETOEY.value,
    )
    KOMMUNE = LanguageStringType(
        en="COUNTY",
        nn=model.UnitType.KOMMUNE.value,
        nb=model.UnitType.KOMMUNE.value,
    )
    KURS = LanguageStringType(
        en="COURSE",
        nn=model.UnitType.KURS.value,
        nb=model.UnitType.KURS.value,
    )
    LOVBRUDD = LanguageStringType(
        en="CRIME",
        nn=model.UnitType.LOVBRUDD.value,
        nb=model.UnitType.LOVBRUDD.value,
    )
    PERSON = LanguageStringType(
        en="PERSON",
        nn=model.UnitType.PERSON.value,
        nb=model.UnitType.PERSON.value,
    )
    STAT = LanguageStringType(
        en="STATE",
        nn=model.UnitType.STAT.value,
        nb=model.UnitType.STAT.value,
    )
    STORFE = LanguageStringType(
        en="CATTLE",
        nn=model.UnitType.STORFE.value,
        nb=model.UnitType.STORFE.value,
    )
    TRAFIKKULYKKE = LanguageStringType(
        en="TRAFFIC ACCIDENT",
        nn=model.UnitType.TRAFIKKULYKKE.value,
        nb=model.UnitType.TRAFIKKULYKKE.value,
    )
    TRANSAKSJON = LanguageStringType(
        en="TRANSACTION",
        nn=model.UnitType.TRANSAKSJON.value,
        nb=model.UnitType.TRANSAKSJON.value,
    )
    VARE_TJENESTE = LanguageStringType(
        en="GOOD/SERVICE",
        nn=model.UnitType.VARE_TJENESTE.value,
        nb=model.UnitType.VARE_TJENESTE.value,
    )
    VERDIPAPIR = LanguageStringType(
        en="SERVICE",
        nn=model.UnitType.VERDIPAPIR.value,
        nb=model.UnitType.VERDIPAPIR.value,
    )
    VIRKSOMHET = LanguageStringType(
        en="BUSINESS",
        nn=model.UnitType.VIRKSOMHET.value,
        nb=model.UnitType.VIRKSOMHET.value,
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
