# (C) Copyright 1996- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import json
import os
import threading
import time

import pytest
import requests
from aviso_rest import logger
from aviso_rest.config import Config
from aviso_rest.frontend import Frontend

from pyaviso.cli_aviso import _parse_inline_params
from pyaviso.notification_manager import NotificationManager

config = Config(conf_path="aviso-server/rest/tests/config.yaml")
frontend_url_home = f"http://{config.host}:{config.port}"
frontend_url_api = f"{frontend_url_home}/api/v1"


@pytest.fixture(scope="module", autouse=True)
def prepost_module():
    # Run the frontend at global level so it will be executed once and accessible to all tests
    frontend = Frontend(config)
    server = threading.Thread(target=frontend.run_server, daemon=True)
    server.start()
    time.sleep(1)
    yield


def test_homepage():
    time.sleep(1)
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    assert requests.get(frontend_url_home).status_code == 500


def test_valid_dissemination_notification():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",  # aviso type indicates how to interpret the "data" payload
        "data": {  # this is aviso specific
            "event": "dissemination",
            "request": {
                "target": "E1",
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",  # location on ceph or s3
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        # UUID random generated by client (maybe reused if request is the same)
        "source": "/host/user",  # together with 'id', uniquely identifies a request
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",  # optional, but recommended
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.ok
    assert resp.status_code == 200
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message")
    assert message.get("message") == "Notification successfully submitted"


def test_valid_mars_notification():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "mars",
            "request": {
                "class": "od",
                "date": "20190810",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
            },
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.ok
    assert resp.status_code == 200
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message")
    assert message.get("message") == "Notification successfully submitted"


def test_bad_request_no_body():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    resp = requests.post(f"{frontend_url_api}/notification")
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Invalid notification, Body cannot be empty"


def test_bad_request_no_id():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "dissemination",
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Missing required attributes: {'id'}"


def test_bad_request_no_source():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "dissemination",
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Missing required attributes: {'source'}"


def test_bad_request_no_spec():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "dissemination",
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Failed to find specversion in HTTP request"


def test_bad_request_no_type():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Invalid notification, 'data' could not be located"


def test_bad_request_no_data():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "data": {
            "event": "dissemination",
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Missing required attributes: {'type'}"


def test_bad_request_no_event():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Invalid notification, 'event' could not be located"


def test_bad_request_no_request():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "dissemination",
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 400
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Invalid notification, 'request' could not be located"


def test_not_found_404():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    resp = requests.post(f"{frontend_url_api}/notFound")
    assert resp.status_code == 404


def test_method_not_allowed_405():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    resp = requests.get(f"{frontend_url_api}/notification")
    assert resp.status_code == 405


def test_notify_ttl():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",  # aviso type indicates how to interpret the "data" payload
        "data": {  # this is aviso specific
            "event": "dissemination",
            "request": {
                "target": "E1",
                "class": "od",
                "date": "20191112",
                "destination": "F",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
            },
            "location": "xxx",  # location on ceph or s3
            "ttl": "1",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        # UUID random generated by client (maybe reused if request is the same)
        "source": "/host/user",  # together with 'id', uniquely identifies a request
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",  # optional, but recommended
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.ok
    assert resp.status_code == 200
    message = resp.json()
    assert message.get("message") == "Notification successfully submitted"

    # now retrieve it
    ps = _parse_inline_params(
        "event=dissemination,target=E1,class=od,date=20191112,destination=F,domain=g,expver=1,step=1,stream=enfo,time=0"
    )
    result = NotificationManager().value(ps, config=config.aviso)
    assert "xxx" in result

    # wait for it to expire
    time.sleep(3)

    # now test the value command
    ps = _parse_inline_params(
        "event=dissemination,target=E1,class=od,date=20191112,destination=F,domain=g,expver=1,step=1,stream=enfo,time=0"
    )
    result = NotificationManager().value(ps, config=config.aviso)
    assert result is None


def test_notify_skip():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",  # aviso type indicates how to interpret the "data" payload
        "data": {  # this is aviso specific
            "event": "dissemination",
            "request": {
                "target": "E1",
                "class": "od",
                "date": "20191112",
                "destination": "FOO",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "cams",
                "time": "0",
            },
            "location": "xxx",  # location on ceph or s3
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        # UUID random generated by client (maybe reused if request is the same)
        "source": "/host/user",  # together with 'id', uniquely identifies a request
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",  # optional, but recommended
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.ok
    assert resp.status_code == 200
    message = resp.json()
    assert message.get("message") == "Notification skipped"


@pytest.mark.skip
# this test is skipped because we cannot change the configuration of the frontend to make him failing
def test_internal_error_500():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "mars",
            "request": {
                "class": "od",
                "date": "20190810",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
            },
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post(f"{frontend_url_api}/notification", json=body)
    assert resp.status_code == 500
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message") == "Internal server error occurred"
    assert message.get("details")


@pytest.mark.skip
def test_send_notification():
    logger.debug(os.environ.get("PYTEST_CURRENT_TEST").split(":")[-1].split(" ")[0])
    body = {
        "type": "aviso",
        "data": {
            "event": "dissemination",
            "request": {
                "class": "od",
                "date": "20190810",
                "destination": "MACI",
                "domain": "g",
                "expver": "1",
                "step": "1",
                "stream": "enfo",
                "time": "0",
                "target": "E1",
            },
            "location": "s3://data.ecmwf.int/diss/foo/bar/20190810/xyz",
        },
        "datacontenttype": "application/json",
        "id": "0c02fdc5-148c-43b5-b2fa-cb1f590369ff",
        "source": "/host/user",
        "specversion": "1.0",
        "time": "2020-03-02T13:34:40.245Z",
    }
    resp = requests.post("http://localhost:30003/api/v1/notification", json=body)
    assert resp.ok
    assert resp.status_code == 200
    assert resp.text
    message = json.loads(resp.text)
    assert message.get("message")
    assert message.get("message") == "Notification successfully submitted"
