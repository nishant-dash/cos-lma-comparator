import logging
import argparse

from .nagios import get_nagios_data, NagiosServices
from .prometheus import get_prometheus_data, PrometheusRules
from .display import list_rules, show_diff, show_summary
from .comparator import compare, summary, identify_duplicates
from .juju_helper import juju_config


def parser():
    parser = argparse.ArgumentParser(
        description='COS LMA Completeness checker',
    )

    parser.add_argument('--juju-lma-controller',
                        default='foundations-maas',
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

    parser.add_argument('--nagios-context',
                        default=None,
                        help='nagios_host_config from `juju config nagios \
                        nagios_host_config`')

    parser.add_argument('--prometheus-url',
                        default=None,
                        help='Instead of auto-detecting the location of \
                        prometheus, use a given URL')

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

    logging.basicConfig(level=logging.INFO)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    nagios_services_json = get_nagios_data(
        args.juju_lma_controller,
        args.juju_lma_model,
        args.juju_lma_user,
    )

    if not args.nagios_context:
        nagios_context = juju_config(
            args.juju_lma_controller,
            args.juju_lma_model,
            args.juju_lma_user,
            "nagios",
            "nagios_host_context"
        )
    else:
        nagios_context = args.nagios_context

    logging.info(f"nagios_context: {nagios_context}")

    nagios_services = NagiosServices(nagios_services_json, nagios_context)

    prometheus_rules_json = get_prometheus_data(
        args.prometheus_url,
        args.juju_cos_controller,
        args.juju_cos_model,
        args.juju_cos_user,
    )
    prometheus_rules = PrometheusRules(prometheus_rules_json, nagios_context)

    print()
    print("Prometheus Duplicates")
    print("=====================")
    identify_duplicates(prometheus_rules.alerts())

    print()
    print("Nagios Duplicates")
    print("=================")
    identify_duplicates(nagios_services.alerts())

    diff_output = compare(
        prometheus_rules.alerts(), nagios_services.alerts()
    )

    summary_output = summary(prometheus_rules.alerts())

    # TODO: Pretty print or json output

    if args.verbose:
        list_rules(prometheus_rules.alerts(), args.format, args.long)

    # TODO: Always show both diff and summary - but later make this listen to
    # options
    show_diff(diff_output, args.format, args.long)
    show_summary(summary_output, args.format)


if __name__ == "__main__":
    main()
