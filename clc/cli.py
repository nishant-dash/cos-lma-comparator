import logging
import argparse

from .nagios import get_nagios_data, NagiosServices
from .prometheus import get_prometheus_data, PrometheusRules
from . import display

from . import comparator


def parser():
    parser = argparse.ArgumentParser(
        description='COS LMA Completeness checker',
    )

    parser.add_argument('--juju-lma-controller',
                        default='foundation-maas',
                        help='Juju LMA controller')

    parser.add_argument('--juju-lma-user',
                        default='admin',
                        help='Juju user')

    parser.add_argument('--juju-lma-model',
                        default='lma-maas',
                        help='Juju LMA model')

    parser.add_argument('--juju-cos-controller',
                        default='microk8s-cos',
                        help='Juju COS controller')

    parser.add_argument('--juju-cos-model',
                        default='cos',
                        help='Juju COS model')

    parser.add_argument('--juju-cos-user',
                        default='admin',
                        help='Juju user')

    parser.add_argument('--prometheus-url',
                        default=None,
                        help='Instead of auto-detecting the location of \
                        prometheus, use a givenkURL')

    parser.add_argument('-f', '--format',
                        default='plain',
                        help='Format for the output')

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help='Enable verbose output')

    parser.add_argument('--long',
                        action='store_true',
                        help="Don't shorten the list of alerts")
    return parser


def main():
    args = parser().parse_args()

    # logging.basicConfig(level=logging.DEBUG)
    # ws_logger = logging.getLogger('websockets.protocol')
    # ws_logger.setLevel(logging.INFO)

    nagios_services_json = get_nagios_data(args)
    logging.debug(nagios_services_json)

    prometheus_rules_json = get_prometheus_data(args)
    logging.debug(prometheus_rules_json)

    nagios_services = NagiosServices(nagios_services_json, args)
    prometheus_rules = PrometheusRules(prometheus_rules_json)

    diff_output = comparator.compare(
        prometheus_rules.alerts(), nagios_services.alerts()
    )
    # summary = comparator.summary(nagios_services.alerts())
    summary = comparator.summary(prometheus_rules.alerts())

    # TODO: Pretty print or json output
    if args.verbose:
        # Also print the list of rules

        # TODO: Organise this better
        print("List of nagios services")
        print("=======================")
        # display.list_rules(nagios_services.alerts(), args)
        display.list_rules(prometheus_rules.alerts(), args)
        print()

    # TODO: Always show both diff and summary - but later make this listen to
    # options
    display.show_diff(diff_output, args)
    display.show_summary(summary, args)


if __name__ == "__main__":
    main()
