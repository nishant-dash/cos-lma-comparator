
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

    prometheus_alerts = set(left_alerts)
    nagios_alerts = set(right_alerts)

    # Alerts in prometheus, but no in nagios
    extra_alerts = prometheus_alerts - nagios_alerts

    # Alerts in nagios, but no in prometheus
    missing_alerts = nagios_alerts - prometheus_alerts

    # Alerts common to both nagios and prometheus
    common_alerts = prometheus_alerts & nagios_alerts

    disagreements = set()
    for alert in missing_alerts.copy():
        # If alert is in both extra and missing that's due its state diverge
        found_alert = [x for x in extra_alerts if x.id() == alert.id()]

        if found_alert:
            extra_alerts.remove(found_alert[0])
            missing_alerts.remove(alert)

            disagreements.add(found_alert[0])
            disagreements.add(alert)

    return {
        "missing_alerts": missing_alerts,
        "extra_alerts": extra_alerts,
        "common_alerts": common_alerts,
        "disagreements": disagreements,
    }


def identify_duplicates(alerts):
    """
    For debugging only. Find the alerts which share the same definition (which
    shouldn't be unique among all alerts).
    """

    seen = set()
    dupes = [alert for alert in alerts if alert in seen or seen.add(alert)]

    [print(str(k), dupes.count(k) + 1) for k in set(dupes)]
    print()

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
