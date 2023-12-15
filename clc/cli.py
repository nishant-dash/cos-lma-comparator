"""COS LMA Completeness checker

This script compares the alerts defined by COS Prometheus rules with
LMA Nagios services.

"""
import logging
import argparse
import json

from .nagios import get_nagios_data, NagiosServices
from .prometheus import get_prometheus_data, PrometheusRules
from .grafana import check_loki_hostnames, check_loki_units, \
    get_loki_logs_filenames
from .display import list_rules, show_diff, show_json, \
    print_title
from .comparator import compare, identify_duplicates
from .juju_helper import juju_config


def parser():
    parser = argparse.ArgumentParser(
        prog='clc',
        description="""
        This script compares the alerts defined by COS Prometheus rules with
        LMA Nagios services.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--juju-lma-controller',
                        default='foundations-maas',
                        help='Juju LMA controller')

    parser.add_argument('--juju-lma-user',
                        default='admin',
                        help='Juju LMA user')

    parser.add_argument('--juju-lma-model',
                        default='lma-maas',
                        help='Juju LMA model')

    parser.add_argument('--juju-cos-controller',
                        default='cos-microk8s-localhost',
                        help='Juju COS controller')

    parser.add_argument('--juju-cos-model',
                        default='cos',
                        help='Juju COS model')

    parser.add_argument('--juju-cos-user',
                        default='admin',
                        help='Juju COS user')

    parser.add_argument('--nagios-context',
                        default=None,
                        help="""Automatically detected from LMA Nagios config
                        nagios_host_config i.e. `juju config nagios
                        nagios_host_config`. Use this argument to override
                        auto-detection.
                        """)

    parser.add_argument('--prometheus-url',
                        default=None,
                        help="""Automatically detected from COS
                        Traefik/Prometheus.
                        Use this argument to override auto-detection.
                        """)

    parser.add_argument('-f', '--format',
                        choices=['plain', 'json'],
                        default='plain',
                        help='Format for the output')

    parser.add_argument('--long',
                        action='store_true',
                        help="""Don't shorten the list of alerts. Print all the
                        duplicates, missing and extra alerts.
                        """)

    parser.add_argument('-d', '--debug',
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG,
                        default=logging.WARNING,
                        help="Print debugging statements",)

    parser.add_argument('-v', '--verbose',
                        action="store_const", dest="loglevel",
                        const=logging.INFO,
                        help="Be verbose",)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--loki-hostnames',
                        action="store_true",
                       help="""Check prometheus hostname labels against juju
                       machines and containers
                       """)

    group.add_argument('--loki-units',
                        action="store_true",
                       help="""Check prometheus instance labels against juju
                       units
                       """)

    group.add_argument('--loki-filenames',
                        action="store_true",
                        help="Print json output of all filenames in Loki",)

    return parser


def main():
    args = parser().parse_args()

    logging.basicConfig(level=args.loglevel)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.WARNING)

    if args.loki_units:
        check_loki_units(
            args.juju_cos_controller,
            args.juju_cos_model,
            args.juju_cos_user,
        )
        return

    if args.loki_hostnames:
        check_loki_hostnames(
            args.juju_cos_controller,
            args.juju_cos_model,
            args.juju_cos_user,
        )
        return

    if args.loki_filenames:
        print(
            json.dumps(
                get_loki_logs_filenames(
                    args.juju_cos_controller,
                    args.juju_cos_model,
                    args.juju_cos_user,
                ),
                indent=2,
            )
        )
        return

    # Fetch Nagios services from thruk-admin API
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

    # Parse Nagios services to NRPE alerts
    nagios_services = NagiosServices(nagios_services_json, nagios_context)

    # Fetch Prometheus rules from Prometheus API
    prometheus_rules_json = get_prometheus_data(
        args.prometheus_url,
        args.juju_cos_controller,
        args.juju_cos_model,
        args.juju_cos_user,
    )
    # Parse Prometheus services to NRPE alerts
    prometheus_rules = PrometheusRules(prometheus_rules_json, nagios_context)

    diff_output = compare(
        prometheus_rules.alerts(), nagios_services.alerts()
    )

    if args.format == 'json':
        print(show_json(diff_output))
        return

    # TODO: Pretty print or json output
    if args.loglevel == logging.INFO:
        print_title("Prometheus Duplicates")
        print()
        identify_duplicates(prometheus_rules.alerts())

        print_title("Nagios Duplicates")
        print()
        identify_duplicates(nagios_services.alerts())

        list_rules(prometheus_rules.alerts(), args.format, args.long)

    # TODO: Always show both diff and summary - but later make this listen to
    # options
    show_diff(diff_output, args.format, args.long)
    # show_summary(summary_output, args.format)


if __name__ == "__main__":
    main()
