import json
import pytest

from clc.nagios import NagiosService, NagiosServices

@pytest.fixture
def nagios_services_json():
    with open("tests/test_data/thruk-agent.services.json") as f:
        return json.load(f)


def test_nagios_service(nagios_services_json):
    service = NagiosService(nagios_services_json[200], "bootstack-abc-defg")
    assert service.juju_unit == "ceph-radosgw/1"
    assert service.alert_check_name == "pacemakerd_proc"


def test_nagios(nagios_services_json):
    assert NagiosServices(nagios_services_json, "bootstack-abc-defg")
