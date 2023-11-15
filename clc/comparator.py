
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

    left_defs = set(left_alerts)
    right_defs = set(right_alerts)

    # assert len(left_defs) == len(left_alerts), "Some left alerts share details which should be unique"
    # assert len(right_defs) == len(right_alerts), "Some right alerts share details which should be unique"

    identify_duplicates(left_alerts)
    identify_duplicates(right_alerts)
    # if not (len(left_defs) == len(left_alerts)):
    #     print("!!!!!!!!!!!!!!!!!!!!!!")
    #     print("Some left alerts share details which should be unique:")

    # if not (len(right_defs) == len(right_alerts)):
    #     print("!!!!!!!!!!!!!!!!!!!!!!")
    #     print("Some right alerts share details which should be unique")

    extra_defs = left_defs - right_defs
    missing_defs = right_defs - left_defs
    common_defs = left_defs & right_defs

    # Only the common alerts can be compared for their exact values
    disagreements = []
    for alert_def in common_defs:
        # Find it in the left and right defs - note the [0] at the end
        # as there should be guaranteed to be exactly one alert.
        prom_alert = [x for x in left_alerts if x == alert_def][0]
        right_alert = [x for x in right_alerts if x == alert_def][0]

        if right_alert.alert_state != prom_alert.alert_state:
            disagreements.append({
                "definition": alert_def,
                "left_state": prom_alert.alert_state,
                "left_time": prom_alert.alert_time,
                "right_state": right_alert.alert_state,
                "right_time": right_alert.alert_time,
            })
        # print("{} vs {} for {}".format(right_alert.alert_state, prom_alert.alert_state, alert_def))

    return {
        "missing_alerts": missing_defs,
        "extra_alerts": extra_defs,
        "disagreements": disagreements,
    }


def identify_duplicates(alerts):
    """
    For debugging only. Find the alerts which share the same definition (which shouldn't be unique among all alerts).
    """

    # Make a dictionary with keys being the "unique" part
    from collections import defaultdict
    d = defaultdict(lambda: [])
    for alert in alerts:
        d[alert].append(alert)

    # Remove all definitions with only one entry - hacky
    for k in list(d.keys()):
        if len(d[k]) == 1:
            del d[k]

    if len(d) == 0:
        return

    print("Duplicate keys")
    print("==============")
    for k, v in d.items():
        print(k, "has duplicates:")
        # Check to see if everything is identical
        if all(vi == v[0] for vi in v):
            print("ALL VALUES (n={}) ARE IDENTICAL IN THEIR DETAIL... WTF???".format(len(v)))
            print(v[0])
        else:
            for alert in v:
                print(" -> ", alert)
        print()


def summary(alerts):
    """
    Summary of the alerts given.

    Output:
      - number of applications
      - number of units
      - number of rules
      - number of rules in error
    """

    def app_name(alert):
        # Note: an app name is determined from its unit name. However, it is also
        # distinguished by the model that it is in.
        app_part = alert.juju_unit.split("/")
        return "{}:{}".format(alert.juju_model, app_part)

    unique_apps = list(app_name(x) for x in alerts)

    # The unit name needs to be distinguished by the model as well
    unique_units = set("{}:{}".format(alert.juju_model, alert.juju_unit) for alert in alerts)

    rules_in_error = [x for x in alerts if x.alert_state != 0]

    return {
        "num_apps": len(unique_apps),
        "num_units": len(unique_units),
        "num_rules": len(alerts),
        "num_rules_alerting": len(rules_in_error),
    }
