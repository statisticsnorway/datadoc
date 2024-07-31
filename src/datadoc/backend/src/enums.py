"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum

from datadoc_model import model
from datadoc_model.model import LanguageStringType
from datadoc_model.model import LanguageStringTypeItem


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
    ) -> str | None:
        """Retrieve the string for the relevant language."""
        if self.language_strings.root is not None:
            for item in self.language_strings.root:
                if item.languageCode == language:
                    return item.languageText
        return None


class Assessment(LanguageStringsEnum):
    """Sensitivity of data."""

    SENSITIVE = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.SENSITIVE.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="SENSITIV"),
            LanguageStringTypeItem(languageCode="nb", languageText="SENSITIV"),
        ],
    )
    PROTECTED = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.PROTECTED.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="SKJERMET"),
            LanguageStringTypeItem(languageCode="nb", languageText="SKJERMET"),
        ],
    )
    OPEN = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.Assessment.OPEN.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="ÅPEN"),
            LanguageStringTypeItem(languageCode="nb", languageText="ÅPEN"),
        ],
    )


class DataSetStatus(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DRAFT = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.DRAFT.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="UTKAST"),
            LanguageStringTypeItem(languageCode="nb", languageText="UTKAST"),
        ],
    )
    INTERNAL = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.INTERNAL.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="INTERN"),
            LanguageStringTypeItem(languageCode="nb", languageText="INTERN"),
        ],
    )
    EXTERNAL = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.EXTERNAL.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="EKSTERN"),
            LanguageStringTypeItem(languageCode="nb", languageText="EKSTERN"),
        ],
    )
    DEPRECATED = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetStatus.DEPRECATED.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="UTGÅTT"),
            LanguageStringTypeItem(languageCode="nb", languageText="UTGÅTT"),
        ],
    )


class DataSetState(LanguageStringsEnum):
    """Processing state of a dataset."""

    SOURCE_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.SOURCE_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="KILDEDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="KILDEDATA"),
        ],
    )
    INPUT_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.INPUT_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="INNDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="INNDATA"),
        ],
    )
    PROCESSED_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.PROCESSED_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="KLARGJORTE DATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="KLARGJORTE DATA"),
        ],
    )
    STATISTICS = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.STATISTICS.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="STATISTIKK"),
            LanguageStringTypeItem(languageCode="nb", languageText="STATISTIKK"),
        ],
    )
    OUTPUT_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataSetState.OUTPUT_DATA.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="UTDATA"),
            LanguageStringTypeItem(languageCode="nb", languageText="UTDATA"),
        ],
    )


class TemporalityTypeType(LanguageStringsEnum):
    """Temporality of a dataset.

    More information about temporality type: https://statistics-norway.atlassian.net/l/c/HV12q90R
    """

    FIXED = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.FIXED.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="FAST"),
            LanguageStringTypeItem(languageCode="nb", languageText="FAST"),
        ],
    )
    STATUS = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.STATUS.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="TVERRSNITT"),
            LanguageStringTypeItem(languageCode="nb", languageText="TVERRSNITT"),
        ],
    )
    ACCUMULATED = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.ACCUMULATED.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="AKKUMULERT"),
            LanguageStringTypeItem(languageCode="nb", languageText="AKKUMULERT"),
        ],
    )
    EVENT = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.TemporalityTypeType.EVENT.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="HENDELSE"),
            LanguageStringTypeItem(languageCode="nb", languageText="HENDELSE"),
        ],
    )


class DataType(LanguageStringsEnum):
    """Simplified data types for metadata purposes."""

    STRING = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.STRING.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="TEKST"),
            LanguageStringTypeItem(languageCode="nb", languageText="TEKST"),
        ],
    )
    INTEGER = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.INTEGER.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="HELTALL"),
            LanguageStringTypeItem(languageCode="nb", languageText="HELTALL"),
        ],
    )
    FLOAT = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.FLOAT.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="DESIMALTALL"),
            LanguageStringTypeItem(languageCode="nb", languageText="DESIMALTALL"),
        ],
    )
    DATETIME = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.DATETIME.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="DATOTID"),
            LanguageStringTypeItem(languageCode="nb", languageText="DATOTID"),
        ],
    )
    BOOLEAN = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.DataType.BOOLEAN.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="BOOLSK"),
            LanguageStringTypeItem(languageCode="nb", languageText="BOOLSK"),
        ],
    )


class IsPersonalData(LanguageStringsEnum):
    """Is the variable instance personal data and if so, how is it encrypted."""

    NOT_PERSONAL_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.NOT_PERSONAL_DATA.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="IKKE PERSONOPPLYSNING",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="IKKE PERSONOPPLYSNING",
            ),
        ],
    )
    PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
        ],
    )
    NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.IsPersonalData.NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="IKKE PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="IKKE PSEUDONYMISERT/KRYPTERT PERSONOPPLYSNING",
            ),
        ],
    )


class VariableRole(LanguageStringsEnum):
    """The role of a variable in a dataset."""

    IDENTIFIER = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.IDENTIFIER.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="IDENTIFIKATOR"),
            LanguageStringTypeItem(languageCode="nb", languageText="IDENTIFIKATOR"),
        ],
    )
    MEASURE = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.MEASURE.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="MÅLEVARIABEL"),
            LanguageStringTypeItem(languageCode="nb", languageText="MÅLEVARIABEL"),
        ],
    )
    START_TIME = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.START_TIME.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="STARTTID"),
            LanguageStringTypeItem(languageCode="nb", languageText="STARTTID"),
        ],
    )
    STOP_TIME = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.STOP_TIME.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="STOPPTID"),
            LanguageStringTypeItem(languageCode="nb", languageText="STOPPTID"),
        ],
    )
    ATTRIBUTE = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.VariableRole.ATTRIBUTE.value,
            ),
            LanguageStringTypeItem(languageCode="nn", languageText="ATTRIBUTT"),
            LanguageStringTypeItem(languageCode="nb", languageText="ATTRIBUTT"),
        ],
    )


class UseRestriction(LanguageStringsEnum):
    """Lifecycle status of a dataset."""

    DELETION_ANONYMIZATION = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.DELETION_ANONYMIZATION.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="SLETTING/ANONYMISERING",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="SLETTING/ANONYMISERING",
            ),
        ],
    )
    PROCESS_LIMITATIONS = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.PROCESS_LIMITATIONS.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="BEHANDLINGSBEGRENSNINGER",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="BEHANDLINGSBEGRENSNINGER",
            ),
        ],
    )
    SECONDARY_USE_RESTRICTIONS = LanguageStringType(
        [
            LanguageStringTypeItem(
                languageCode="en",
                languageText=model.UseRestriction.SECONDARY_USE_RESTRICTIONS.value,
            ),
            LanguageStringTypeItem(
                languageCode="nn",
                languageText="SEKUNDÆRBRUKSRESTRIKSJONER",
            ),
            LanguageStringTypeItem(
                languageCode="nb",
                languageText="SEKUNDÆRBRUKSRESTRIKSJONER",
            ),
        ],
    )
