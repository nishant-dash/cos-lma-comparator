import json
import requests
import juju_helper

from juju import jasyncio

from structures import NRPEData


class PrometheusAlertRule():
    def __init__(self, rule):
        for k, v in rule.items():
            setattr(self, k, v)

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def extractCommand(self):
        prefix = "avg_over_time(command_status{command="
        if self.query.startswith(prefix):
            self.command = self.query[len(prefix):].split('"')[1].strip()
        else:
            pass
            # TODO log error
            raise Exception("TODO: This should log an error. Could not parse command from prometheus output: {}".format(self.query))

    def isNrpeRule(self):
        return self.name.endswith("NrpeAlert")

    def exportToComparator(self):
        return NRPEData(
            juju_unit = self.labels["juju_unit"],
            juju_model = self.labels["juju_model"],
            alert_state = 42,
            alert_check_name = self.command,
            alert_time = 0,
        )


def fetch_rules_raw(url):
    '''
    Fetch the list of all rules from the Prometheus endpoint and return it as a
    parsed dictionary.

    url: string - the prometheus endpoint without trailing slash, e.g. http://10.123.456.78:80/cos-prometheus-0
    '''

    response = requests.get(url + "/api/v1/rules")
    if not response.ok:
        raise Exception("Unable to fetch rules from endpoint")

    return response.json()

def parse(prom_raw):
    '''
    Parse the raw dictionary from Prometheus and return a list of rules as
    PrometheusAlertRule objects.

    prom_raw - the json parsed input from the prometheus endpoint
    '''

    rules = []
    for r in prom_raw["data"]["groups"]:
        rules += r['rules']

    nrpes = []
    for r in rules:
        rule = PrometheusAlertRule(r)
        if not rule.isNrpeRule():
            continue
        rule.extractCommand()
        nrpes += [rule.exportToComparator()]

    return nrpes


def get_prometheus_url(args):
    traefik_proxied_endpoints_action_raw = jasyncio.run(
        juju_helper.connect_model_run_command(
            controller_name=args.juju_cos_controller,
            model_name=args.juju_cos_model,
            user=args.juju_cos_user,
            app_name='traefik',
            command='show-proxied-endpoints',
            action=True,
        )
    )

    traefik_proxied_endpoints_json = json.loads(
        traefik_proxied_endpoints_action_raw['proxied-endpoints']
    )

    for k,v in traefik_proxied_endpoints_json.items():
        if k.startswith("prometheus"):
            return v["url"]

    raise Exception("Unable to find URL for prometheus in traefik endpoints")


def get_prometheus_data(args):
    if args.prometheus_url is None:
       url = get_prometheus_url(args)
    else:
       url = args.prometheus_url
    # url = "http://10.169.129.59:80/cos-prometheus-0"
    
    prometheus_metrics_json = fetch_rules_raw(url)
    
    rules = parse(prometheus_metrics_json)

    return rules
