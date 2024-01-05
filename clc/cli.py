"""COS LMA Completeness checker

This script compares the alerts defined by COS Prometheus rules with
LMA Nagios services.

"""
import logging
import argparse
import json

from .grafana import check_loki_hostnames, check_loki_units, \
    get_loki_logs_filenames
from .display import list_rules, show_json, print_title, show_diff
from .comparator import identify_duplicates, check_nagios_alerts


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

    group.add_argument('--grafana-dashboards',
                       action="store_true",
                       help="Check Grafana dashboards against LMA and COS",)

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

    if args.grafana_dashboards:
        check_grafana_dashboards()
        return

    nagios_alerts_output = check_nagios_alerts(
        args.juju_lma_controller,
        args.juju_lma_model,
        args.juju_lma_user,
        args.juju_cos_controller,
        args.juju_cos_model,
        args.juju_cos_user,
        args.nagios_context,
        args.prometheus_url,
    )

    if args.format == 'json':
        print(show_json(nagios_alerts_output ))
        return
    show_diff(nagios_alerts_output, args.format, args.long)

if __name__ == "__main__":
    main()
