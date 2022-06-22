# Purpose:
# I want a sas dataset in /datadoc/tests/resources
# To achieve this I must run .create_testdata.sas with SASPy
# It requires a SAS OnDemand for Academics account and some config

# TODO: If not exists; add file datadoc\tests\resources\sascfg_personal.py to local directory
# TODO: If not exists; add file template _authinfo (win) or .authinfo (mac) to user home directory
#       Do something if password is not present in this file? Or will this generate an error anyway?

import saspy
from pathlib import PurePath

def setup_module():
    sas_session = saspy.SASsession()
    code = open(PurePath('./datadoc/tests/create_testdata.sas')).read()
    global log_submit
    log_submit = sas_session.submit(code)
    global log_download
    remote_file = sas_session.workpath + 'sasdata.sas7bdat'
    log_download = sas_session.download(PurePath('./datadoc/tests/resources/sasdata.sas7bdat'), remote_file)

    # TODO: Could this be useful?
    sasdata = sas_session.sasdata("sasdata")
    columnInfo = sasdata.columnInfo()
    print(type(columnInfo))
    print(columnInfo)

    sas_session.endsas()


def test_submit_noerror():
    error = False
    if 'ERROR' in log_submit['LOG']:
        error = True
    assert error is False


def test_download_success():
    assert log_download['Success'] is True


# TODO: Possible tests:
# TODO: Check log_submit for 'ERROR'
# TODO: Assert log_download has Succcess == True
# TODO: Read SAS dataset with sas7bdat
# TODO: Check structure of SAS-dataset