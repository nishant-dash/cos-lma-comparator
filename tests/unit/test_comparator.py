from clc.comparator import compare, identify_duplicates
from clc.nrpedata import NRPEData


def test_compare():
    alert1 = NRPEData(juju_unit="app-unit/0", alert_check_name="check-alert-0")
    alert2 = NRPEData(juju_unit="app-unit/1", alert_check_name="check-alert-1")
    extra = NRPEData(juju_unit="app-unit/2", alert_check_name="check-alert-2")
    missing = NRPEData(juju_unit="app-unit/3", alert_check_name="check-alert-3")

    left = [
        alert1,
        alert2,
        extra,
    ]

    right = [
        alert1,
        alert2,
        missing,
    ]

    expected_extra_alerts = set([extra])
    expected_missing_alerts = set([missing])

    output = compare(left, right)
    assert output["missing_alerts"] == expected_missing_alerts
    assert output["extra_alerts"] == expected_extra_alerts


def test_disagreement():
    alert1 = NRPEData(juju_unit="app-unit/0", alert_check_name="check-alert-0",
                      alert_state=0)
    alert2 = NRPEData(juju_unit="app-unit/1", alert_check_name="check-alert-1",
                      alert_state=0)
    extra = NRPEData(juju_unit="app-unit/2", alert_check_name="check-alert-2")
    missing = NRPEData(juju_unit="app-unit/3", alert_check_name="check-alert-3")

    from dataclasses import replace
    alert2b = replace(alert2, alert_state=2)

    left_alerts = [
        alert1,
        alert2,
        extra,
    ]
    right_alerts = [
        alert1,
        alert2b,
        missing,
    ]

    output = compare(left_alerts, right_alerts)

    expected_disagreements = set([alert2, alert2b])
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
