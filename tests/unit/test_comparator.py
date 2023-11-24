import pytest

from clc.comparator import compare, identify_duplicates
from clc.nrpedata import NRPEData


def test_compare():
    alert1 = NRPEData(juju_unit="app-unit/0", alert_check_name="check-alert-0")
    alert2 = NRPEData(juju_unit="app-unit/1", alert_check_name="check-alert-1")
    alert3 = NRPEData(juju_unit="app-unit/2", alert_check_name="check-alert-2")
    alert4 = NRPEData(juju_unit="app-unit/3", alert_check_name="check-alert-3")

    left = [
        alert1,
        alert2,
        alert3,
    ]

    right = [
        alert1,
        alert2,
        alert4,
    ]

    expected_extra_alerts = set([alert3])
    expected_missing_alerts = set([alert4])

    output = compare(left, right)
    assert output["missing_alerts"] == expected_missing_alerts
    assert output["extra_alerts"] == expected_extra_alerts


def test_long_compare():
    alert1 = NRPEData(juju_model="openstack", alert_identifier="octavia",
                      alert_check_name="lbs", alert_state=0)

    alert2 = NRPEData(juju_model="openstack", alert_identifier="n-c-c",
                      alert_check_name="VMs", alert_state=1)

    alert3 = NRPEData(juju_model="openstack2", alert_identifier="n-c-c",
                      alert_check_name="VMs", alert_state=1)

    missing = NRPEData(juju_model="openstack", alert_identifier="keystone",
                      alert_check_name="Idunno", alert_state=0)

    extra = NRPEData(juju_model="mymodel", alert_identifier="myunit",
                      alert_check_name="myalert", alert_state=2)

    from dataclasses import replace
    alert3b = replace(alert3, alert_state=2)

    left_alerts = [
        alert1,
        alert2,
        alert3,
        extra,
    ]
    right_alerts = [
        alert1,
        alert2,
        alert3b,
        missing,
    ]

    output = compare(left_alerts, right_alerts)

    assert output["missing_alerts"] == set([missing])
    assert output["extra_alerts"] == set([extra])

    expected_disagreements = [{
       "definition": alert3,
       "left_state": alert3.alert_state,
       "right_state": alert3b.alert_state,
    }]
    assert output["disagreements"] == expected_disagreements


def test_identify_duplicates():
    alert1 = NRPEData(juju_unit="app-unit/0", alert_check_name="check-alert-1")
    alert2 = NRPEData(juju_unit="app-unit/1", alert_check_name="check-alert-2")

    alerts = [
        alert1,
        alert1,
        alert1,
        alert2,
    ]

    expect_dupe = identify_duplicates(alerts)

    assert expect_dupe[0] == alert1
    assert alert2 not in expect_dupe
