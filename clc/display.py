from .nrpedata import NRPEData

TRUNCATE_THRESHOLD = 20


def list_rules(alerts, out_format, long_format):
    # TODO: Organise this better
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print_truncatable_list(
        "List of nagios services",
        alerts,
        lambda alert: print(alert),
        long_format,
    )
    print()


def show_diff(diff_output, out_format, long_format):
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    missing_alerts = diff_output["missing_alerts"]
    extra_alerts = diff_output["extra_alerts"]
    common_alerts = diff_output["common_alerts"]
    disagreements = diff_output["disagreements"]

    print_truncatable_list(
        "Rules missing in prometheus",
        sorted(missing_alerts),
        lambda alert: print(alert),
        long_format,
    )

    print_truncatable_list(
        "Extra rules in prometheus not present in nagios",
        sorted(extra_alerts),
        lambda alert: print(alert),
        long_format,
    )

    print_truncatable_list(
        "Alerts with different alert status",
        sorted(disagreements),
        lambda alert: print(alert),
        long_format,
    )

    print_title("Summary")
    print()
    print(f"extra_alerts: {len(extra_alerts)}")
    print(f"missing_alerts: {len(missing_alerts)}")
    print(f"common_alerts: {len(common_alerts)}")
    print(f"disagreements: {len(disagreements)}")


def show_summary(summary, out_format):
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print(summary)


def print_truncatable_list(title, lst, print_func, long_format):
    print_title(title)

    prev_alert = NRPEData()
    if not long_format:
        for item in lst:
            if prev_alert.alert_identifier != item.alert_identifier:
                print()
                print(item.alert_identifier, end=': ')
            print(item.alert_check_name, end=' ')
            prev_alert = item
        print()
    else:
        for item in lst:
            print_func(item)
    print()


def show_json(diff_output):
    missing_alerts = diff_output["missing_alerts"]
    extra_alerts = diff_output["extra_alerts"]
    common_alerts = diff_output["common_alerts"]
    disagreements = diff_output["disagreements"]

    return {
        "missing_alerts": dict(map(lambda x: x.to_json(), missing_alerts)),
        "extra_alerts": dict(map(lambda x: x.to_json(), extra_alerts)),
        "common_alerts": dict(map(lambda x: x.to_json(), common_alerts)),
        "disagreements": dict(map(lambda x: x.to_json(), disagreements)),
    }


def print_title(title):
    print("-" * len(title))
    print(title)
    print("-" * len(title), end='')
