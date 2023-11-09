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

    def definition(self):
        """
        Export a tuple with the fields that are identifiers and should be
        unique amongst all alerts from this monitoring service.
        """
        return (self.juju_model, self.juju_unit, self.alert_check_name)
