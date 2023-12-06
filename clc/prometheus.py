import json
import logging
import re
import requests

from . import juju_helper
from .nrpedata import NRPEData


class PrometheusRule(NRPEData):
    """PrometheusRule define an alert coming from Prometheus.

    Args:
        prometheus_service_json: A single rule element from Prometheus API json
            output
        nagios_context: A string that is prepended to instance name to set the
            host name in nagios.

    Attributes:
        _{*}: All attributes parsed from json are available to the class
            instance as `_attribute_name`. i.e. self._host_name
        nagios_context: Same as args.
        alert_identifier: Alert identifier use to match
            {nagios_context}-{app_name}-{unit_number},
            i.e. bootstack-foo-bar-mysql-0
        alert_check_name: Alert command name without the prefix `check_`.
            i.e.: load
    """
    def __init__(self, prometheus_rule_json, nagios_context):
        super().__init__()

        self.set_json(prometheus_rule_json)
        self.nagios_context = nagios_context

        __juju_unit = self._labels.get("juju_unit", None)
        if __juju_unit:
            self.alert_identifier = __juju_unit.replace('/', '-')
            self.juju_unit = __juju_unit.replace(nagios_context+'-', '')

        self.alert_check_name = self.__extract_command()
        self.alert_state = self.__extract_alert_state()

        logging.debug(f"{__juju_unit} {self._query}")

    def __extract_alert_state(self):
        if hasattr(self, '_alerts') and self._alerts:
            return int(float(self._alerts[-1]["value"]))
        else:
            return 0

    def __extract_command(self):
        extract_command = re.search('command=\"([^"]+)\",', self._query)
        if extract_command:
            return extract_command.group(1).replace('check_', '')
        else:
            logging.info(f"Could not parse prometheus rule command: \
                            {self._query}")
            return ""

    def is_nrpe_rule(self):
        return self._name.endswith("NrpeAlert")


class PrometheusRules:
    def __init__(self, prometheus_rules_json, nagios_context=None):
        '''
        Parse the raw dictionary from Prometheus /rules API and store each rule
        as PrometheusRule objects.

        Args:
            prometheus_rules_json: JSON when querying Prometheus /api/v1/rules
            nagios_context: A string that is prepended to instance name to set
                the host name in nagios.
        '''
        self._alerts = []

        for group in prometheus_rules_json["data"]["groups"]:
            for r in group['rules']:
                nrpe_data = PrometheusRule(r, nagios_context)
                nrpe_data._group_name = group["name"]
                nrpe_data._group_file = group["file"]
                if nrpe_data.is_nrpe_rule():
                    self._alerts.append(nrpe_data)

    def alerts(self):
        return sorted(list(self._alerts))


def get_prometheus_url(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
):
    """Fetch into Traefik juju application the prometheus URL"""
    try:
        traefik_proxied_endpoints_raw = juju_helper.juju_run_action(
            controller_name=juju_cos_controller,
            model_name=juju_cos_model,
            user=juju_cos_user,
            app_name='traefik',
            command='show-proxied-endpoints'
        )

        first_key = list(traefik_proxied_endpoints_raw.keys())[0]
        traefik_proxied_endpoints_json = json.loads(
            traefik_proxied_endpoints_raw[first_key]['results']['proxied-endpoints' ]
        )

        for k, v in traefik_proxied_endpoints_json.items():
            if k.startswith("prometheus"):
                return v["url"]
    except Exception as e:
        print(e)
        print("Error fetching nagios data. Please check your Juju model, controller and user")
        return

    raise Exception("Unable to find URL for prometheus in traefik endpoints")


def get_prometheus_data(
    prometheus_url=None,
    juju_cos_controller=None,
    juju_cos_model=None,
    juju_cos_user=None,
):
    """Fetch the list of all rules from the Prometheus endpoint and return it
    as a parsed dictionary.

    prometheus_url: string - the prometheus endpoint without trailing slash,
        e.g. http://10.123.456.78:80/cos-prometheus-0

    If prometheus_url is None it will try to retrieve the URL from COS model
    """
    if prometheus_url is None:
        url = get_prometheus_url(
            juju_cos_controller,
            juju_cos_model,
            juju_cos_user,
        )
    else:
        url = prometheus_url

    response = requests.get(url + "/api/v1/rules")
    if not response.ok:
        raise Exception("Unable to get rules from prometheus endpoint")

    return response.json()
