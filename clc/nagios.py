import json
#from juju import jasyncio

from .utils import juju_helper
from .utils.structures import NRPEData


class NagiosService(NRPEData):
    def __init__(self, nagios_service_json, nagios_context=None):
        super().__init__()
        self.set_json(nagios_service_json)

        self.nagios_context = nagios_context

        self.juju_unit = self.__extract_unit_name()
        self.alert_check_name = self._host_check_command

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def __context_match(self):
        if self.nagios_context is None:
            return False
        return self._host_display_name.startswith(self.nagios_context)

    def __extract_unit_name(self):
        if self.__context_match():
            return self._host_display_name[len(self.nagios_context)+1:].replace("-", "/")
        else:
            return self._host_display_name

    def __extract_app_name(self):
        if self.juju_unit:
            return self.juju_unit.split("/")[0]


class NagiosServices:
    def __init__(self, nagios_services_json, args, nagios_context=None):
        self._alerts = []

        for service in nagios_services_json:
            self._alerts.append(NagiosService(service, nagios_context))

    def alerts(self):
        return list(self._alerts)



from subprocess import check_output, DEVNULL
import shlex
import json

def json_call(command):
    raw = check_output(shlex.split(command), stderr=DEVNULL)
    j = json.loads(raw)
    return j    

def get_nagios_data(args):
    j = json_call("juju controllers --format json")
    controllers = list(j["controllers"].keys())
    
    for c in controllers:
        j = json_call("juju models --controller {} --format json".format(c))
        models = [x["name"] for x in j["models"]]

        for m in models:
            j = json_call("juju status --model {}:{} --format json".format(c,m))
            if "thruk-agent" in j["applications"]:
                # This is what we want
                j = json_call("juju exec --format json -m {}:{} --unit thruk-agent/0 -- sudo thruk r /services".format(c,m))
                output = j[0]["stdout"]

                data = json.loads(output)
                return data
    raise Exception("Couldn't find model")
