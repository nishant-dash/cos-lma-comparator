from rules import PrometheusClient
from services import NagiosClient

nagios_host_context = "bootstack-***REMOVED***-***REMOVED***"

prom_data = PrometheusClient()
nagios_data = NagiosClient(nagios_host_context)

rules = prom_data.rules
services = nagios_data.services

cos_units = {}
for r in rules:
    cos_units.add(r.juju_unit)

nagios_units = set()
for s in services:
    nagios_units.add(s.juju_unit)

for u in nagios_units:
    if not u in cos_units:
        print(f"{u} is missing in COS alerts")

