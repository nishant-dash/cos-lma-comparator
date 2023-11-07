import json

# juju run -u thruk-agent/leader -- thruk r '/services'
with open('thruk-agent.services.json') as f:
    raw_data = json.load(f)


rules = []
for service in raw_data:
    rules += [{
        "unit": service['host_name'],
        "name": service['host_check_command'],
        "command": service['check_command'],
    }]

print(rules)
