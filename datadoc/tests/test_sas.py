# TODO: Could this be useful?
# sasdata = sas_session.sasdata("sasdata")
# columnInfo = sasdata.columnInfo()


import saspy
from pathlib import PurePath
from .utils import TEST_SAS_FILEPATH, TEST_SAS_PROGRAM


def setup_module():
    global sas_session
    sas_session = saspy.SASsession()


def run_sas_program(sas_session):
    code = open(PurePath(TEST_SAS_PROGRAM)).read()
    return sas_session.submit(code)


def download_sas_dataset(sas_session):
    remote_file = sas_session.workpath + PurePath(TEST_SAS_FILEPATH).name
    return sas_session.download(PurePath(TEST_SAS_FILEPATH), remote_file)


def test_submit_noerrorinlog():
    run_log = run_sas_program(sas_session)
    error = False
    if 'ERROR' in run_log['LOG']:
        error = True
    assert error is False


def test_download_success():
    run_log = run_sas_program(sas_session)
    download_log = download_sas_dataset(sas_session)
    assert download_log['Success'] is True


def teardown_module():
    sas_session.endsas()


# TODO: Possible tests:
# TODO: Read SAS dataset with sas7bdat
# TODO: Check structure of SAS-dataset
