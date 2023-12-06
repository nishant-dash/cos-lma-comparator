import json
import logging
import re

from . import juju_helper
from .nrpedata import NRPEData


class NagiosService(NRPEData):
    """NagiosService define an alert coming from nagios.

    Args:
        nagios_service_json: A single element from Nagios /services json output
        nagios_context: A string that is prepended to instance name to set the
            host name in nagios.

    Attributes:
        _{*}: All attributes parsed from json are available to the class
            instance as `_attribute_name`. i.e. self._host_name
        nagios_context: Same as args.
        alert_identifier: Alert identifier {nagios_context}-{app_name}-{unit_number},
            i.e. bootstack-foo-bar-mysql-0
        alert_check_name: Alert command name without the prefix `check_`.
            i.e.: load
        juju_unit: Best effort on extracting juju unit name from alerts
    """

    def __init__(self, nagios_service_json, nagios_context=None):
        super().__init__()
        self.set_json(nagios_service_json)

        self.nagios_context = nagios_context

        self.alert_identifier = self._host_display_name
        self.juju_unit = self.__extract_unit_name()
        self.alert_check_name = self.__extract_command()

        self.alert_state = self._state

        logging.debug(f"{self._host_display_name} {self._display_name}")

    def __extract_unit_name(self):
        extract_unit = re.search(f"{self.nagios_context}-(.*)-[0-9]+",
                                 self._host_display_name)
        if extract_unit:
            names = self._host_display_name.split('-')
            return extract_unit.group(1) + '/' + names[-1]

    def __extract_command(self):
        extract_command = re.search(f"{self._host_display_name}-(.*)",
                                    self._display_name)
        if extract_command:
            return extract_command.group(1).replace('check_', '')
        else:
            logging.debug(f"Could not parse nagios command: \
                            {self._display_name}")
            return ""

    def __extract_app_name(self):
        if self.juju_unit:
            return self.juju_unit.split("/")[0]


class NagiosServices:
    def __init__(self, nagios_services_json, nagios_context=None):
        self._alerts = []

        for service in nagios_services_json:
            nagios_service = NagiosService(service, nagios_context)
            if nagios_service.alert_check_name != "":
                self._alerts.append(nagios_service)

    def alerts(self):
        return list(self._alerts)


def get_nagios_data(
    juju_lma_controller,
    juju_lma_model,
    juju_lma_user,
):
    """Use juju ssh to query nagios API using thruk CLI agent"""
    try:
        nagios_services = juju_helper.juju_ssh(
            controller_name=juju_lma_controller,
            model_name=juju_lma_model,
            user=juju_lma_user,
            app_name='thruk-agent',
            command='sudo thruk r /services',
        )
        return json.loads(nagios_services)
    except Exception as e:
        print(e)
        print("Error fetching nagios data. Please check your Juju model, controller and user")
        return
