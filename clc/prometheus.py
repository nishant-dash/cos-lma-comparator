import json
import re
import requests

from .utils import juju_helper
from .utils.structures import NRPEData


class PrometheusRule(NRPEData):
    def __init__(self, prometheus_rule_json):
        super().__init__(self)

        self.set_json(prometheus_rule_json)

        self.juju_model = self._labels.get("juju_model", None)
        self.juju_unit = self._labels.get("nrpe_unit", None)

        if self.is_nrpe_rule():
            self.alert_check_name = self.__extract_command()

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def __extract_command(self):
        extract_command = re.search('command=\"([^"]+)\",', self._query)
        if extract_command:

            return extract_command.group(1)
        else:
            raise Exception("Could not parse command from prometheus output: {}".format(self._query))

    def is_nrpe_rule(self):
        return self._name.endswith("NrpeAlert")


class PrometheusRules:
    def __init__(self, prometheus_rules_json):
        '''
        Parse the raw dictionary from Prometheus and return a list of rules as
        PrometheusAlertRule objects.

        prom_raw - the json parsed input from the prometheus endpoint
        '''
        self._alerts = []

        for group in prometheus_rules_json["data"]["groups"]:
            for r in group['rules']:
                nrpe_data = PrometheusRule(r)
                nrpe_data._group_name = group["name"]
                nrpe_data._group_file = group["file"]
                if nrpe_data.is_nrpe_rule():
                    self._alerts.append(nrpe_data)

    def alerts(self):
        return list(self._alerts)


def fetch_prometheus_json(url):
    '''
    Fetch the list of all rules from the Prometheus endpoint and return it as a
    parsed dictionary.

    url: string - the prometheus endpoint without trailing slash, e.g. http://10.123.456.78:80/cos-prometheus-0
    '''

    response = requests.get(url + "/api/v1/rules")
    if not response.ok:
        raise Exception("Unable to fetch rules from endpoint")

    return response.json()


def get_prometheus_url(args):
    traefik_proxied_endpoints_action_raw = juju_helper.juju_run_action(
            controller_name=args.juju_cos_controller,
            model_name=args.juju_cos_model,
            user=args.juju_cos_user,
            app_name='traefik',
            command='show-proxied-endpoints'
    )

    first_key = list(traefik_proxied_endpoints_action_raw.keys())[0]
    traefik_proxied_endpoints_json = json.loads(
        traefik_proxied_endpoints_action_raw[first_key]['results']['proxied-endpoints']
    )

    for k, v in traefik_proxied_endpoints_json.items():
        if k.startswith("prometheus"):
            return v["url"]

    raise Exception("Unable to find URL for prometheus in traefik endpoints")


def get_prometheus_data(args):
    if args.prometheus_url is None:
        url = get_prometheus_url()
    else:
        url = args.prometheus_url
    return fetch_prometheus_json(url)
