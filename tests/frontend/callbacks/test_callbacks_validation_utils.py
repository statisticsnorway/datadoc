# def test_validation_utils()


from unittest import mock

import dash_bootstrap_components as dbc
from dapla_metadata.datasets import Datadoc

from datadoc import state
from datadoc.frontend.callbacks.utils import save_metadata_and_generate_alerts
from datadoc.frontend.components.builders import AlertTypes
from datadoc.frontend.components.builders import build_ssb_alert


# if none metadata missing: only save alert
# if dataset missing ->
# if variables missing ->
# if another warning ->
# if not n_clicks ?
def test_save_and_validate(metadata: Datadoc, mocker):
    # if n_clicks and n_clicks > 0 ?

    success_alert = build_ssb_alert(
        AlertTypes.SUCCESS,
        "Lagret metadata",
    )
    state.metadata = metadata

    mocker.patch(
        "datadoc.frontend.callbacks.utils.save_metadata_and_generate_alerts",
        return_value=success_alert,
    )
    output = save_metadata_and_generate_alerts(metadata)
    assert isinstance(output, list)
    num_list_of_alerts = 3
    assert len(output) == num_list_of_alerts
    assert output[1] is not None


def test_with_mock_patch(metadata_3):
    state.metadata = metadata_3
    result = save_metadata_and_generate_alerts(metadata_3)
    num_list_of_alerts = 3
    assert len(result) == num_list_of_alerts
    assert result[1] is None
    assert result[2] is None


def test_1():
    mock_metadata = mock.Mock()
    mock_metadata.variables = [
        "var1",
        "var2",
    ]
    state.metadata = mock_metadata

    result = save_metadata_and_generate_alerts(
        mock_metadata,
    )

    num_list_of_alerts = 3
    assert len(result) == num_list_of_alerts
    assert result[2] is None
    assert isinstance(result[0], dbc.Alert)
