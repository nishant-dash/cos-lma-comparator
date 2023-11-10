
def list_rules(alerts, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")
    for alert in alerts:
        print("Alert {}".format(alert.definition()))

def show_diff(diff_output, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print("Rules missing from prometheus")
    print("=============================")
    for alert in diff_output["missing_alerts"]:
        print(alert)
    print()

    print("Extra rules in prometheus not present in nagios")
    print("===============================================")
    for alert in diff_output["extra_alerts"]:
        print(alert)
    print()

    print("Alerts with different alert status")
    print("==================================")
    for output in diff_output["disagreements"]:
        print(output)
    print()

def show_summary(summary, args):
    if args.format != "plain":
        raise NotImplementedError("Non-plain output for all alerts is TODO")

    print(summary)
