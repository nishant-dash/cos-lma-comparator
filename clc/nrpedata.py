import json
from dataclasses import dataclass

@dataclass
class NRPEData:
    # These are identifiers - they must be unique
    juju_model: str = None
    juju_unit: str = None
    alert_check_name: str = None

    # These are 'variable' they may different between requests
    alert_state: int = None
    alert_time: float = None

    def set_json(self, raw_alert_json):
        for k, v in raw_alert_json.items():
            setattr(self, "_" + k, v)

    def __hash__(self):
        """
        Export a tuple with the fields that are identifiers and should be
        unique amongst all alerts from this monitoring service.
        """
        return hash((self.juju_unit, self.alert_check_name))

    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               str(self) == str(other)

    def __str__(self):
        return "{}-{}".format(self.juju_unit, self.alert_check_name)
