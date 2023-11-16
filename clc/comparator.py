import logging


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

    left_defs  = set(left_alerts)
    right_defs = set(right_alerts)

    extra_defs = left_defs - right_defs
    missing_defs = right_defs - left_defs
    common_defs = left_defs & right_defs

    logging.info(f"extra_alerts: {len(extra_defs)}")
    logging.info(f"missing_alerts: {len(missing_defs)}")
    logging.info(f"common_alerts: {len(common_defs)}")

    # Only the common alerts can be compared for their exact values
    disagreements = []
    for alert_def in common_defs:
        # Find it in the left and right defs - note the [0] at the end
        # as there should be guaranteed to be exactly one alert.
        prom_alert = [x for x in left_alerts if x == alert_def][0]
        right_alert = [x for x in right_alerts if x == alert_def][0]

        if right_alert.alert_state != prom_alert.alert_state:
            disagreements.append({
                "definition": str(alert_def),
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
    For debugging only. Find the alerts which share the same definition (which
    shouldn't be unique among all alerts).
    """

    seen = set()
    dupes = [alert for alert in alerts if alert in seen or seen.add(alert)]

    print()
    print("Duplicate alerts")
    print("==============")
    [print(str(k), dupes.count(k) + 1) for k in set(dupes)]

    return dupes


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
        return alert.juju_unit.split("/")[0]

    unique_apps = set(app_name(x) for x in alerts)

    # The unit name needs to be distinguished by the model as well
    unique_units = set("{}:{}".format(alert.juju_model, alert.juju_unit) for alert in alerts)

    rules_in_error = [x for x in alerts if x.alert_state != 0]

    return {
        "num_apps": len(unique_apps),
        "num_units": len(unique_units),
        "num_rules": len(alerts),
        "num_rules_alerting": len(rules_in_error),
    }
