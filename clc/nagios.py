import json

from .utils import juju_helper
from .utils.structures import NRPEData


class NagiosService(NRPEData):
    def __init__(self, sc, context):
        self.nagios_context = context
        self.__extractUnitName()

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)

    def __haveMatchingContext(self):
        return self.host_display_name.startswith(self.nagios_context)

    def __extractUnitName(self):
        if self.__haveMatchingContext():
            self.juju_unit = self.host_display_name[len(self.nagios_context)+1:].replace("-", "/")
        else:
            self.juju_unit = None

    def __extractAppName(self):
        if self.juju_unit:
            self.app_name = self.juju_unit.splint("/")[0]


class NagiosServices:
    def __init__(self, nagios_services_json):
        self._alerts = set()

        for r in nagios_services_json:
            self._alerts.append(NagiosService(r))


def get_nagios_data(args):
    nagios_services_json = juju_helper.juju_ssh(
            controller_name=args.juju_lma_controller,
            model_name=args.juju_lma_model,
            user=args.juju_lma_user,
            app_name='thruk-agent',
            command='thruk r /services',
        )
    return nagios_services_json
