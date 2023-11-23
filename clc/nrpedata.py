import json
from dataclasses import dataclass, asdict


@dataclass
class NRPEData:
    """Common class to compare alerts from Nagios services and Prometheus alert
    rules

    Comparison is done through `alert_identifier` and `alert_check_name` attributes

    Attributes:
        alert_identifier: Alert identifier {nagios_context}-{app_name}-{unit_number},
            i.e. bootstack-foo-bar-mysql-0
        alert_check_name: Alert command name without the prefix `check_`.
            i.e.: load
    """
    # These are identifiers - they must be unique
    alert_identifier: str = None
    alert_check_name: str = None

    juju_model: str = None
    juju_unit: str = None

    # These are 'variable' they may different between requests
    alert_state: int = None
    alert_time: float = None

    def set_json(self, raw_alert_json):
        """Convert every JSON attribute to a private object attribute."""
        for k, v in raw_alert_json.items():
            setattr(self, "_" + k, v)

    def to_json(self):
        return json.dumps(asdict(self))

    def __str__(self):
        return ":".join([
            str(self.juju_model or ''),
            str(self.alert_identifier or ''),
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
            self.alert_identifier,
            self.alert_check_name,
            self.alert_state,
        ))

    def __lt__(self, other):
        return str(self) < str(other)

    def __eq__(self, other):
        return isinstance(other, NRPEData) and \
            self.juju_model == other.juju_model and \
            self.alert_identifier == other.alert_identifier and \
            self.alert_check_name == other.alert_check_name and \
            self.alert_state == other.alert_state
