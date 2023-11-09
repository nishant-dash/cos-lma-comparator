from structures import NRPEData

def compare(left_alerts, right_alerts):
    """
    Compare the alerts obtained from two different sources (these are expected
    to be prometheus and nagios for now) and output a dictionary containing:
    - extra_alerts: the alerts that are present in "left" but missing in "right"
    - missing alerts: the alerts that are present in "right" but missing in "left"
    - disagreements: the alerts which are common but disagree in their status.

    left_alerts: set of NRPEData
    right_alerts: set of NRPEData
    """

    # If the data is exactly the same, we should be able to do:
    #   extra_alerts = left_alerts - right_alerts
    #   missing_alerts = right_alerts - left_alerts
    # But since we have time to compare with, this might be a problem. Also we
    # might want to see which ones are different in terms of alerts.

    # The set of {juju_model, juju_unit, alert_check_name} is the "definition/identifier"
    # of the NRPEData. The {alert_state, alert_time} are variable "measurements".

    left_defs = set(x.definition() for x in left_alerts)
    right_defs = set(x.definition() for x in right_alerts)

    assert len(left_defs) == len(left_alerts), "Some left alerts share details which should be unique"
    assert len(right_defs) == len(right_alerts), "Some right alerts share details which should be unique"

    extra_defs = left_defs - right_defs
    missing_defs = right_defs - left_defs
    common_defs = left_defs & right_defs

    # Only the common alerts can be compared for their exact values
    disagreements = []
    for alert_def in common_defs:
        # Find it in the left and right defs - note the [0] at the end
        # as there should be guaranteed to be exactly one alert.
        prom_alert = [x for x in left_alerts if x.definition() == alert_def][0]
        right_alert = [x for x in right_alerts if x.definition() == alert_def][0]
        
        if right_alert.alert_state != prom_alert.alert_state:
            disagreements.append({
                "definition": alert_def,
                "left_state": prom_alert.alert_state,
                "left_time": prom_alert.alert_time,
                "right_state": right_alert.alert_state,
                "right_time": right_alert.alert_time,
            })
        #print("{} vs {} for {}".format(right_alert.alert_state, prom_alert.alert_state, alert_def))

    return {
        "missing_alerts": missing_defs,
        "extra_alerts": extra_defs,
        "disagreements": disagreements,
    }






def test_compare():
    alert1 = NRPEData(juju_model="openstack", juju_unit="octavia", alert_check_name="lbs", alert_state=0, alert_time=42)
    alert2 = NRPEData(juju_model="openstack", juju_unit="n-c-c", alert_check_name="VMs", alert_state=1, alert_time=43)
    alert3 = NRPEData(juju_model="openstack2", juju_unit="n-c-c", alert_check_name="VMs", alert_state=1, alert_time=43)
    alert4 = NRPEData(juju_model="openstack", juju_unit="keystone", alert_check_name="Idunno", alert_state=0, alert_time=43)
    alert1repeat = NRPEData(juju_model="openstack", juju_unit="octavia", alert_check_name="lbs", alert_state=0, alert_time=102)

    # alert b just have a different time, except for alert4 which differs
    from dataclasses import replace
    alert1b = replace(alert1, alert_time=50)
    alert2b = replace(alert2, alert_time=51)
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
    try:
        compare(left_alerts + [alert1repeat], right_alerts)
    except AssertionError as exc:
        print("Expected AssertError, hurray! {}".format(exc))
        pass
    else:
        print("Should have failed but didn't!")
    try:
        compare(left_alerts, right_alerts + [alert1repeatb])
    except AssertionError as exc:
        print("Expected AssertError, hurray! {}".format(exc))
        pass
    else:
        print("Should have failed but didn't!")

    output = compare(left_alerts, right_alerts)
    print(output)

    if output["missing_alerts"] == set([alert3b.definition()]):
        print("Successfully identified missing alerts")
    else:
        print("FAILED!!! identified missing alerts")

    if output["extra_alerts"] == set([alert2.definition()]):
        print("Successfully identified extra alerts")
    else:
        print("FAILED!!! identified extra alerts")

    if output["disagreements"] == [ {
            "definition": alert4.definition(),
            "left_state": alert4.alert_state,
            "left_time": alert4.alert_time,
            "right_state": alert4b.alert_state,
            "right_time": alert4b.alert_time,
    } ]:
        print("Successfully identified disagreeing alerts")
    else:
        print("FAILED!!! identified disagreeing alerts")

if __name__ == "__main__":
    test_compare()
