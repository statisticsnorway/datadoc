from __future__ import annotations


class StatisticSubjectMapping:
    """Allow mapping between statistic short name and primary and secondary subject."""

    def __init__(self, source_url: str | None = None) -> None:
        """Retrieves the statistical structure document from the given URL.

        Initializes the mapping dicts. Based on the values in the statistical structure document.
        """
        self.source_url = source_url
        self.secondary_subject_primary_subject_mapping: dict[str, str] = {"al03": "al"}
        self.statistic_short_name_secondary_subject_mapping: dict[str, str] = {
            "nav_statres": "al03",
        }

    def get_primary_subject(self, statistic_short_name: str) -> str | None:
        """Returns the primary subject for the given statistic short name by mapping it through the secondary subject.

        Looks up the secondary subject for the statistic short name, then uses that
        to look up the corresponding primary subject in the mapping dict.

        Returns the primary subject string if found, else None.
        """
        if seconday_subject := self.get_secondary_subject(statistic_short_name):
            return self.secondary_subject_primary_subject_mapping.get(
                seconday_subject,
                None,
            )

        return None

    def get_secondary_subject(self, statistic_short_name: str) -> str | None:
        """Looks up the secondary subject for the given statistic short name in the mapping dict.

        Returns the secondary subject string if found, else None.
        """
        return self.statistic_short_name_secondary_subject_mapping.get(
            statistic_short_name,
            None,
        )

    @staticmethod
    def _fetch_statistical_structure_document(source_url: str) -> dict:
        pass

    @staticmethod
    def _build_secondary_subject_primary_subject_mapping() -> dict[str, str]:
        pass

    @staticmethod
    def _build_statistic_short_name_secondary_subject_mapping() -> dict[str, str]:
        pass
