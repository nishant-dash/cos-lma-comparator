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

    def __str__(self):
        return ":".join([
            str(self.juju_model or ''),
            str(self.juju_unit or ''),
            str(self.alert_check_name or ''),
            str('' if self.alert_state is None else self.alert_state),
            str('' if self.alert_time is None else self.alert_time),
        ])

    def __hash__(self):
        """
        Export a tuple with the fields that are identifiers and should be
        unique amongst all alerts from this monitoring service.
        """
        return hash((
            self.juju_model,
            self.juju_unit,
            self.alert_check_name,
            self.alert_state,
        ))

    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return isinstance(other, NRPEData) and \
            self.juju_model == other.juju_model and \
            self.juju_unit == other.juju_unit and \
            self.alert_check_name == other.alert_check_name and \
            self.alert_state == other.alert_state
