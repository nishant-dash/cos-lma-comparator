TRUNCATE_THRESHOLD = 20


def list_rules(alerts, out_format, long_format):
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print_truncatable_list(
        alerts,
        lambda alert: print("Alert {}".format(alert.definition())),
        long_format,
    )


def show_diff(diff_output, out_format, long_format):
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print("Rules missing from prometheus")
    print("=============================")
    print_truncatable_list(
        sorted(diff_output["missing_alerts"]),
        lambda alert: print(alert),
        long_format,
    )
    print()

    print("Extra rules in prometheus not present in nagios")
    print("===============================================")
    print_truncatable_list(
        sorted(diff_output["extra_alerts"]),
        lambda alert: print(alert),
        long_format,
    )
    print()

    print("Alerts with different alert status")
    print("==================================")
    print_truncatable_list(
        sorted(diff_output["disagreements"]),
        lambda output: print(output),
        long_format,
    )
    print()


def show_summary(summary, out_format):
    if out_format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print(summary)


def print_truncatable_list(lst, print_func, long_format):
    truncate_amount = int(TRUNCATE_THRESHOLD/2)
    if not long_format and len(lst) > TRUNCATE_THRESHOLD:
        for item in lst[:truncate_amount]:
            print_func(item)
        print("..... {} rules omitted .....".format(len(lst) - truncate_amount*2))
        for item in lst[-truncate_amount:]:
            print_func(item)
    else:
        for item in lst:
            print_func(item)
