import json
import requests

class PrometheusAlertRule():
    def __init__(self, rule):
        for k, v in rule.items():
            setattr(self, k, v)

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def extractCommand(self):
        if self.query.startswith("avg_over_time(command_status{command="):
            self.command = self.query[37:].split('"')[1].strip()
        else:
            pass
            #TODO log error
    
    def isNrpeRule(self):
        return self.name.endswith("NrpeAlert")

    def exportToComparator(self):
        return {
            "name": self.name,
            "command": self.command,
            "unit": self.labels["juju_unit"],
            "model": self.labels["juju_model"]
        }

def parse_rule(rule):
    rule = PrometheusAlertRule(rule)
    if rule.isNrpeRule():
        rule.extractCommand()
        return rule.exportToComparator()


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
        nrpes += [rule]

    return nrpes
