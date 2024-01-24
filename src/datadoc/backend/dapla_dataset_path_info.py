"""Extract info from an path following SSB`s naming convention."""
import datetime
import pathlib


class DaplaDatasetPathInfo:
    """Extract info from an path following SSB`s naming convention."""

    def __init__(self, dataset_path: str) -> None:
        """Read info from an path following SSB`s naming convention."""
        self.dataset_path = pathlib.Path(dataset_path)
        self.dataset_name_sections = self.dataset_path.stem.split("_")

    @property
    def contains_data_from(self) -> datetime.date:
        """Read dataset from date in ISO format year-month-day."""
        return
