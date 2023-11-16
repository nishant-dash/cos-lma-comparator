import json
import re

from . import juju_helper
from .nrpedata import NRPEData


class NagiosService(NRPEData):
    def __init__(self, nagios_service_json, nagios_context=None):
        super().__init__()
        self.set_json(nagios_service_json)

        self.nagios_context = nagios_context

        self.juju_unit = self.__extract_unit_name()
        self.alert_check_name = self.__extract_check_command()

    def __context_match(self):
        return bool(re.search(self.nagios_context, self._host_display_name))

    def __extract_unit_name(self):
        if self.__context_match():
            names = self._host_display_name[len(self.nagios_context)+1:].split('-')
            return '-'.join(names[:-1]) + '/' + names[-1]
        else:
            return self._host_display_name

    def __extract_check_command(self):
        return self._display_name[len(self.nagios_context)+1+len(self.juju_unit)+1:]
            #raise Exception("Could not parse command from nagios display_name: {}".format(self._display_name))

    def __extract_app_name(self):
        if self.juju_unit:
            return self.juju_unit.split("/")[0]


class NagiosServices:
    def __init__(self, nagios_services_json, nagios_context=None):
        self._alerts = []

        for service in nagios_services_json:
            self._alerts.append(NagiosService(service, nagios_context))

    def alerts(self):
        return list(self._alerts)


def get_nagios_data(
    juju_lma_controller,
    juju_lma_model,
    juju_lma_user,
):
    nagios_services = juju_helper.juju_ssh(
        controller_name=juju_lma_controller,
        model_name=juju_lma_model,
        user=juju_lma_user,
        app_name='thruk-agent',
        command='sudo thruk r /services',
    )
    return json.loads(nagios_services)
