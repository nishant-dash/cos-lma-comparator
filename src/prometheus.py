import json

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

with open('rules.json') as r:
    rules_raw = json.load(r)

rules = []
for r in rules_raw["data"]["groups"]:
    rules += r['rules']

for r in rules:
    rule = PrometheusAlertRule(r)
    if rule.isNrpeRule():
        print(rule.state)

#for r in rules:
#    data = parse_rule(r)
#    if data:
#        print(json.dumps(data, indent=2))