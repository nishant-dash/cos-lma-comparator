from clc.comparator import summary
from clc.utils.structures import NRPEData

def test_summary():
    def make_test_nrpe(**kwargs):
        return NRPEData(**kwargs)

    alerts = [
        make_test_nrpe(juju_model="openstack", juju_unit="octavia", alert_check_name="lbs", alert_state=0, alert_time=42),
        make_test_nrpe(juju_model="openstack", juju_unit="n-c-c", alert_check_name="VMs", alert_state=1, alert_time=43),
        make_test_nrpe(juju_model="openstack", juju_unit="n-c-c", alert_check_name="VMs2", alert_state=1, alert_time=43),
        make_test_nrpe(juju_model="openstack", juju_unit="n-c-c", alert_check_name="VMs3", alert_state=1, alert_time=43),
        make_test_nrpe(juju_model="openstack", juju_unit="keystone", alert_check_name="Idunno", alert_state=0, alert_time=43),
        make_test_nrpe(juju_model="openstack", juju_unit="vault", alert_check_name="Idunno", alert_state=0, alert_time=43),
        make_test_nrpe(juju_model="lma", juju_unit="vault", alert_check_name="Idunno", alert_state=0, alert_time=43),
    ]

    output = summary(alerts)

    print(output)
    expected_output = {'num_apps': 5, 'num_rules': 7, 'num_rules_alerting': 3, 'num_units': 5}
    assert output == expected_output
