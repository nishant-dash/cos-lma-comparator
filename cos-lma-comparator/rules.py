import json

class PrometheusAlertRule():
    def __init__(self, rule):
        for k, v in rule.items():
            setattr(self, k, v)
        if self.__isNrpeRule():
            self.nrpe_command = self.__extractCommand()
        else:
            self.nrpe_command = None
        self.juju_unit = self.labels.get("juju_unit", None)

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def __extractCommand(self):
        if self.query.startswith("avg_over_time(command_status{command="):
            self.command = self.query[37:].split('"')[1].strip()
        else:
            pass
            #TODO log error
    
    def __isNrpeRule(self):
        return self.name.endswith("NrpeAlert")

    def exportToComparator(self):
        return {
            "name": self.name,
            "command": self.command,
            "unit": self.labels["juju_unit"],
            "model": self.labels["juju_model"]
        }

class PrometheusClient:
    def __init__(self):
        self.fetchPrometheusData()

    def fetchPrometheusData(self):
        with open('rules.json') as r:
            rules_raw = json.load(r)

        rules = []
        for r in rules_raw["data"]["groups"]:
            rules += r['rules']

        self.rules = []
        for r in rules:
            rule = PrometheusAlertRule(r)
            if rule.nrpe_command:
                self.rules.append(rule)