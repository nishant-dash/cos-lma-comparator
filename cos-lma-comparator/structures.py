from dataclasses import dataclass

@dataclass
class NRPEData:
    juju_model: str
    juju_unit: str
    alert_state: int # Maybe str?
    alert_check_name: str
    alert_time: float # Unix time

    def __init__(self, raw_alert_json):
        for k, v in raw_alert_json.items():
            setattr(self, "_" + k, v)
