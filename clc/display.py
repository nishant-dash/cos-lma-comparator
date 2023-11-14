TRUNCATE_THRESHOLD = 20


def list_rules(alerts, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print_truncatable_list(
        alerts,
        lambda alert: print("Alert {}".format(alert.definition())),
        args
    )


def show_diff(diff_output, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print("Rules missing from prometheus")
    print("=============================")
    print_truncatable_list(
        sorted(diff_output["missing_alerts"]),
        lambda alert: print(alert),
        args
    )
    print()

    print("Extra rules in prometheus not present in nagios")
    print("===============================================")
    print_truncatable_list(
        sorted(diff_output["extra_alerts"]),
        lambda alert: print(alert),
        args
    )
    print()

    print("Alerts with different alert status")
    print("==================================")
    print_truncatable_list(
        sorted(diff_output["disagreements"]),
        lambda output: print(output),
        args
    )
    print()


def show_summary(summary, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print(summary)


def print_truncatable_list(lst, print_func, args):
    truncate_amount = int(TRUNCATE_THRESHOLD/2)
    if not args.long and len(lst) > TRUNCATE_THRESHOLD:
        for item in lst[:truncate_amount]:
            print_func(item)
        print("..... {} rules omitted .....".format(len(lst) - truncate_amount*2))
        for item in lst[-truncate_amount:]:
            print_func(item)
    else:
        for item in lst:
            print_func(item)
