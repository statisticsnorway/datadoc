"""Test function build_dataset_edit_section."""

import functools

import dash_bootstrap_components as dbc
import pytest
import ssb_dash_components as ssb  # type: ignore[import-untyped]
from dash import html
from datadoc_model import model

from datadoc import enums
from datadoc.enums import SupportedLanguages
from datadoc.frontend.components.builders import build_dataset_edit_section
from datadoc.frontend.fields.display_base import INPUT_KWARGS
from datadoc.frontend.fields.display_base import DatasetDropdownField
from datadoc.frontend.fields.display_base import DatasetInputField
from datadoc.frontend.fields.display_base import get_enum_options_for_language
from datadoc.frontend.fields.display_base import get_metadata_and_stringify
from datadoc.frontend.fields.display_dataset import NON_EDITABLE_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import OPTIONAL_DATASET_METADATA
from datadoc.frontend.fields.display_dataset import DatasetIdentifiers


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    [
        (
            "Obligatorisk",
            NON_EDITABLE_DATASET_METADATA,
            SupportedLanguages.NORSK_BOKMÅL,
            model.Dataset(short_name="fantastic_dataset"),
            {"type": "dataset-edit-section", "id": "obligatory-nb"},
        ),
        (
            "",
            [],
            SupportedLanguages.NORSK_BOKMÅL,
            model.Dataset(short_name="fantastic_dataset"),
            {"type": "dataset-edit-section", "id": "obligatory-nb"},
        ),
        (
            "",
            [],
            "",
            model.Dataset(short_name="amazing_dataset"),
            {"type": "dataset-edit-section", "id": "obligatory-nb"},
        ),
        (
            "",
            [],
            "",
            model.Dataset(short_name="unbelievable_dataset"),
            {},
        ),
        (
            "",
            [],
            "",
            model.Dataset(),
            {},
        ),
        (
            "",
            [],
            "",
            None,
            {},
        ),
        (
            "Amazing title",
            [],
            SupportedLanguages.ENGLISH,
            None,
            {},
        ),
        (
            "New title",
            OPTIONAL_DATASET_METADATA,
            SupportedLanguages.NORSK_NYNORSK,
            model.Dataset(),
            {},
        ),
    ],
)
def test_build_dataset_section(title, field_types, language, dataset, key):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    assert edit_section is not None
    assert isinstance(edit_section, html.Section)


@pytest.mark.parametrize(
    ("title", "field_types", "language", "dataset", "key"),
    [
        (
            "Obligatorisk",
            NON_EDITABLE_DATASET_METADATA,
            SupportedLanguages.NORSK_BOKMÅL,
            model.Dataset(short_name="fantastic_dataset"),
            {"type": "dataset-edit-section", "id": "obligatory-nb"},
        ),
        (
            "",
            [],
            "",
            model.Dataset(short_name="unbelievable_dataset"),
            {},
        ),
        (
            "",
            [],
            "",
            model.Dataset(),
            {},
        ),
        (
            "",
            [],
            "",
            None,
            {},
        ),
        (
            "Amazing title",
            [],
            SupportedLanguages.ENGLISH,
            None,
            {},
        ),
        (
            "New title",
            OPTIONAL_DATASET_METADATA,
            SupportedLanguages.NORSK_NYNORSK,
            model.Dataset(),
            {},
        ),
        (
            "New title",
            {},
            SupportedLanguages.NORSK_BOKMÅL,
            model.Dataset(short_name="last_dataset"),
            {},
        ),
        (
            "New title",
            [
                DatasetInputField(
                    identifier=DatasetIdentifiers.SHORT_NAME.value,
                    display_name="Kortnavn",
                    description="Navn på (fysisk) datafil, datatabell eller datasett",
                    obligatory=True,
                    editable=False,
                ),
                DatasetDropdownField(
                    identifier=DatasetIdentifiers.DATASET_STATUS.value,
                    display_name="Status",
                    description="Livssyklus for datasettet",
                    options_getter=functools.partial(
                        get_enum_options_for_language,
                        enums.DataSetStatus,
                    ),
                    obligatory=True,
                ),
                DatasetDropdownField(
                    identifier=DatasetIdentifiers.DATASET_STATE.value,
                    display_name="Datatilstand",
                    description="Datatilstand. Se Intern dokument 2021- 17  Datatilstander i SSB",
                    obligatory=True,
                    options_getter=functools.partial(
                        get_enum_options_for_language,
                        enums.DataSetState,
                    ),
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.NAME.value,
                    display_name="Navn",
                    description="Datasettnavn",
                    obligatory=True,
                    multiple_language_support=True,
                    value_getter=get_metadata_and_stringify,
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.DATA_SOURCE.value,
                    display_name="Datakilde",
                    description="Datakilde. Settes enten for datasettet eller variabelforekomst.",
                    obligatory=True,
                    multiple_language_support=True,
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.POPULATION_DESCRIPTION.value,
                    display_name="Populasjon",
                    description="Populasjonen datasettet dekker. Populasjonsbeskrivelsen inkluderer enhetstype, geografisk dekningsområde og tidsperiode.",
                    obligatory=True,
                    multiple_language_support=True,
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.VERSION.value,
                    display_name="Versjon",
                    description="Versjon",
                    extra_kwargs=dict(type="number", min=1, **INPUT_KWARGS),
                    obligatory=True,
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.VERSION_DESCRIPTION.value,
                    display_name="Versjonsbeskrivelse",
                    description="Årsak/grunnlag for denne versjonen av datasettet i form av beskrivende tekst.",
                    multiple_language_support=True,
                    obligatory=True,
                ),
                DatasetDropdownField(
                    identifier=DatasetIdentifiers.TEMPORALITY_TYPE.value,
                    display_name="Temporalitetstype",
                    description="Temporalitetstype. Settes enten for variabelforekomst eller datasett. Se Temporalitet, hendelser og forløp.",
                    options_getter=functools.partial(
                        get_enum_options_for_language,
                        enums.TemporalityTypeType,
                    ),
                    obligatory=True,
                ),
                DatasetInputField(
                    identifier=DatasetIdentifiers.DESCRIPTION.value,
                    display_name="Beskrivelse",
                    description="Beskrivelse av datasettet",
                    multiple_language_support=True,
                    obligatory=True,
                ),
            ],
            SupportedLanguages.NORSK_BOKMÅL,
            model.Dataset(short_name="last_dataset"),
            {},
        ),
    ],
)
def test_build_dataset_form(title, field_types, language, dataset, key):
    edit_section = build_dataset_edit_section(
        title,
        field_types,
        language,
        dataset,
        key,
    )
    dataset_form = edit_section.children[1]
    inputs = [element for element in dataset_form if isinstance(element, ssb.Input)]
    assert edit_section._children_props is not None  # noqa: SLF001
    assert isinstance(edit_section.children[0], ssb.Title)
    assert isinstance(dataset_form, dbc.Form)
    for item in inputs:
        assert isinstance(item, ssb.Input)
    for item in inputs:
        assert item.debounce is True