import logging
import argparse

from prometheus import get_prometheus_data
from nagios import get_nagios_data


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
    return parser


if __name__ == "__main__":
    args = parser().parse_args()

    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    nagios_services_json = get_nagios_data(args)
    logging.debug(nagios_services_json)

    prometheus_alerts_json = get_prometheus_data(args)
    logging.debug(prometheus_alerts_json)
