from dataclasses import dataclass

@dataclass
class NRPEData:
    juju_model: str
    juju_unit: str
    alert_state: int # Maybe str?
    alert_check_name: str
    alert_time: float # Unix time


