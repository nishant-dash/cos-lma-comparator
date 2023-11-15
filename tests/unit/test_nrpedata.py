from clc.nrpedata import NRPEData


def test_nrpedata():
    alert = NRPEData(juju_model="model",
                     juju_unit="app-unit/0",
                     alert_check_name="check-name",
                     alert_state=0,
                     alert_time=1)

    assert str(NRPEData()) == "::::"
    assert str(alert) == "model:app-unit/0:check-name:0:1"


def test_nrpedata_eq():

    alert1 = NRPEData(juju_model="model",
                      juju_unit="app-unit/0",
                      alert_check_name="check-name",
                      alert_state=0,
                      alert_time=1)

    alert2 = NRPEData(juju_model="model",
                      juju_unit="app-unit/0",
                      alert_check_name="check-name",
                      alert_state=0,
                      alert_time=1)

    alert_set = set()
    alert_set.add(alert1)
    alert_set.add(alert2)

    assert alert1 == alert2
    assert len(alert_set) == 1
