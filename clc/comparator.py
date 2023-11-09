
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




