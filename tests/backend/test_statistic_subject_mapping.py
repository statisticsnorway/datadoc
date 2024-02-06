import pytest

from datadoc.backend.statistic_subject_mapping import StatisticSubjectMapping


@pytest.fixture()
def statistic_subject_mapping() -> StatisticSubjectMapping:
    return StatisticSubjectMapping()


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_primary_subject"),
    [("nav_statres", "al"), ("unknown_name", None)],
)
def test_get_primary_subject(
    statistic_subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_primary_subject: str,
) -> None:
    assert (
        statistic_subject_mapping.get_primary_subject(statistic_short_name)
        == expected_primary_subject
    )


@pytest.mark.parametrize(
    ("statistic_short_name", "expected_secondary_subject"),
    [("nav_statres", "al03"), ("unknown_name", None)],
)
def test_get_secondary_subject(
    statistic_subject_mapping: StatisticSubjectMapping,
    statistic_short_name: str,
    expected_secondary_subject: str,
) -> None:
    assert (
        statistic_subject_mapping.get_secondary_subject(statistic_short_name)
        == expected_secondary_subject
    )
