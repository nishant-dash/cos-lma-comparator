import pytest

from clc.comparator import compare
from clc.nrpedata import NRPEData


def test_compare():
    alert1 = NRPEData(juju_model="model",
                      juju_unit="app-unit/0",
                      alert_check_name="check-name",
                      alert_state=0,
                      alert_time=1)

    alert2 = NRPEData(juju_model="model",
                      juju_unit="app-unit/0",
                      alert_check_name="check-name",
                      alert_state=0,
                      alert_time=1)

    assert compare([alert1],[alert2])

def test_long_compare():
    alert1 = NRPEData(juju_model="openstack", juju_unit="octavia", alert_check_name="lbs", alert_state=0, alert_time=42)
    alert2 = NRPEData(juju_model="openstack", juju_unit="n-c-c", alert_check_name="VMs", alert_state=1, alert_time=43)
    alert3 = NRPEData(juju_model="openstack2", juju_unit="n-c-c", alert_check_name="VMs", alert_state=1, alert_time=43)
    alert4 = NRPEData(juju_model="openstack", juju_unit="keystone", alert_check_name="Idunno", alert_state=0, alert_time=43)
    alert1repeat = NRPEData(juju_model="openstack", juju_unit="octavia", alert_check_name="lbs", alert_state=0, alert_time=102)

    # alert b just have a different time, except for alert4 which differs
    from dataclasses import replace
    alert1b = replace(alert1, alert_time=50)
#    alert2b = replace(alert2, alert_time=51)
    alert3b = replace(alert3, alert_time=52)
    alert4b = replace(alert4, alert_time=53, alert_state=2)
    alert1repeatb = replace(alert1repeat, alert_time=53)

    left_alerts = [
        alert1,
        alert2,
        alert4,
    ]
    right_alerts = [
        alert1b,
        alert3b,
        alert4b,
    ]

    # We should get assertion error when there's a duplicate
    with pytest.raises(AssertionError):
        compare(left_alerts + [alert1repeat], right_alerts)
    with pytest.raises(AssertionError):
        compare(left_alerts, right_alerts + [alert1repeatb])

    output = compare(left_alerts, right_alerts)

    assert output["missing_alerts"] == set([alert3b])
    assert output["extra_alerts"] == set([alert2])

    expected_disagreements = [{
            "definition": alert4,
            "left_state": alert4galert_state,
            "left_time": alert4.alert_time,
            "right_state": alert4b.alert_state,
            "right_time": alert4b.alert_time,
    }]
    assert output["disagreements"] == expected_disagreements
