from enum import Enum


class SupportedLanguages(str, Enum):
    "Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
    NORSK_BOKMÅL = "nb"
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"
