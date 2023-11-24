import pytest
import json
from clc.nrpedata import NRPEData
from clc.nagios import NagiosService
from clc.prometheus import PrometheusRule


@pytest.fixture()
def prom_alert_rule_json():
    prom_rule = r"""{
    "state": "firing",
    "name": "CheckNovaServicesNrpeAlert",
    "query": "avg_over_time(command_status{command=\"check_nova_services\",juju_unit=\"bootstack-abcd-efgh-openstack-service-checks/0\"}[15m]) > 1 or (absent_over_time(up{juju_unit=\"bootstack-abcd-efgh-openstack-service-checks/0\"}[10m]) == 1)",
    "duration": 0,
    "keepFiringFor": 0,
    "labels": {
    "juju_application": "bootstack-abcd-efgh-openstack-service-checks",
    "juju_model": "openstack",
    "juju_unit": "bootstack-abcd-efgh-openstack-service-checks/0",
    "nrpe_application": "nrpe-lxd",
    "nrpe_unit": "nrpe-lxd/33",
    "severity": "critical"
    },
    "annotations": {
    "description": "Check provided by nrpe_exporter in model {{ $labels.juju_model }} is failing.\nFailing check = {{ $labels.command }}\nUnit = {{ $labels.juju_unit }}\nValue = {{ $value }}\nLegend:\n  - StatusOK       = 0\n  - StatusWarning  = 1\n  - StatusCritical = 2\n  - StatusUnknown  = 3",
    "summary": "Unit {{ $labels.juju_unit }}: {{ $labels.command }} critical."
    },
    "alerts": [
    {
    "labels": {
    "alertname": "CheckNovaServicesNrpeAlert",
    "command": "check_nova_services",
    "dns_name": "juju-0f5ecd-3-lxd-19.maas",
    "host": "1.2.3.4",
    "instance": "1.2.3.4:5666",
    "job": "juju_openstack_1d47aba_bootstack_abcd_efgh_openstack_service_checks_0_check_nova_services_prometheus_scrape",
    "juju_application": "bootstack-abcd-efgh-openstack-service-checks",
    "juju_model": "openstack",
    "juju_model_uuid": "1d47abaf-7b7b-4403-821c-21d82d0f5ecd",
    "juju_unit": "bootstack-abcd-efgh-openstack-service-checks/0",
    "nrpe_application": "nrpe-lxd",
    "nrpe_unit": "nrpe-lxd/33",
    "severity": "critical"
    },
    "annotations": {
    "description": "Check provided by nrpe_exporter in model openstack is failing.\nFailing check = check_nova_services\nUnit = bootstack-abcd-efgh-openstack-service-checks/0\nValue = 2\nLegend:\n  - StatusOK       = 0\n  - StatusWarning  = 1\n  - StatusCritical = 2\n  - StatusUnknown  = 3",
    "summary": "Unit bootstack-abcd-efgh-openstack-service-checks/0: check_nova_services critical."
    },
    "state": "firing",
    "activeAt": "2023-11-09T12:02:33.495816741Z",
    "value": "2e+00"
    }
    ],
    "health": "ok",
    "evaluationTime": 0.001124269,
    "lastEvaluation": "2023-11-24T14:26:33.537662237Z",
    "type": "alerting"
    }
    """
    return json.loads(prom_rule)


@pytest.fixture()
def prom_rule_json():
    prom_rule = r"""{
    "state": "inactive",
    "name": "CheckTelegrafHttpNrpeAlert",
    "query": "avg_over_time(command_status{command=\"check_telegraf_http\",juju_unit=\"bootstack-hijk-lmn-etcd/2\"}[15m]) > 1 or (absent_over_time(up{juju_unit=\"bootstack-hijk-lmn-etcd/2\"}[10m]) == 1)",
    "labels": {
    "juju_application": "bootstack-hijk-lmn-etcd",
    "juju_model": "openstack",
    "juju_unit": "bootstack-hijk-lmn-etcd/2",
    "nrpe_application": "nrpe-container",
    "nrpe_unit": "nrpe-container/4",
    "severity": "critical"
    },
    "annotations": {
    "description": "Check provided by nrpe_exporter in model {{ $labels.juju_model }} is failing.\nFailing check = {{ $labels.command }}\nUnit = {{ $labels.juju_unit }}\nValue = {{ $value }}\nLegend:\n  - StatusOK       = 0\n  - StatusWarning  = 1\n  - StatusCritical = 2\n  - StatusUnknown  = 3",
    "summary": "Unit {{ $labels.juju_unit }}: {{ $labels.command }} critical."
    },
    "health": "ok",
    "evaluationTime": 0.000791422,
    "lastEvaluation": "2023-11-07T09:36:04.455213581Z",
    "alerts": [],
    "type": "alerting"
    }
    """
    return json.loads(prom_rule)


@pytest.fixture()
def nagios_alert_service_json():
    nagios_service = r"""{
    "accept_passive_checks": 1,
    "acknowledged": 1,
    "action_url": "",
    "action_url_expanded": "",
    "active_checks_enabled": 1,
    "check_command": "check_nrpe_H_HOSTADDRESS__ccheck_nova_services_t10!",
    "check_interval": 5,
    "check_options": 0,
    "check_period": "24x7",
    "check_type": 0,
    "checks_enabled": 1,
    "comments": [ 1986, 1989 ],
    "contact_groups": [ "admins" ],
    "contacts": [ "pagerduty", "root" ],
    "current_attempt": 4,
    "current_notification_number": 1,
    "custom_variable_names": [],
    "custom_variable_values": [],
    "custom_variables": {},
    "description": "bootstack-abcd-efgh-openstack-service-checks-0-nova_services",
    "display_name": "bootstack-abcd-efgh-openstack-service-checks-0-nova_services",
    "event_handler": "",
    "event_handler_enabled": 1,
    "execution_time": 1.082148,
    "first_notification_delay": 0,
    "flap_detection_enabled": 1,
    "groups": [],
    "has_been_checked": 1,
    "high_flap_threshold": 0,
    "host_accept_passive_checks": 1,
    "host_acknowledged": 0,
    "host_action_url_expanded": "",
    "host_active_checks_enabled": 1,
    "host_address": "1.2.3.4",
    "host_alias": "bootstack-abcd-efgh-openstack-service-checks-0",
    "host_check_command": "check-host-alive",
    "host_check_type": 0,
    "host_checks_enabled": 1,
    "host_comments": [],
    "host_current_attempt": 1,
    "host_custom_variable_names": [],
    "host_custom_variable_values": [],
    "host_custom_variables": {},
    "host_display_name": "bootstack-abcd-efgh-openstack-service-checks-0",
    "host_groups": [ "bootstack-abcd-efgh-openstack-service-checks", "all" ],
    "host_has_been_checked": 1,
    "host_icon_image_alt": "Ubuntu Linux",
    "host_icon_image_expanded": "base/ubuntu.png",
    "host_is_executing": 0,
    "host_is_flapping": 0,
    "host_last_state_change": 1694422605,
    "host_latency": 0.159,
    "host_name": "bootstack-abcd-efgh-openstack-service-checks-0",
    "host_notes_url_expanded": "",
    "host_notifications_enabled": 1,
    "host_parents": [ "bootstack-abcd-efgh-hostopqnmq" ],
    "host_perf_data": "rta=19.044001ms;5000.000000;5000.000000;0.000000 pl=0%;100;100;0",
    "host_pl": "0",
    "host_pl_unit": "%",
    "host_plugin_output": "PING OK - Packet loss = 0%, RTA = 19.04 ms",
    "host_rta": "19.044001",
    "host_rta_unit": "ms",
    "host_scheduled_downtime_depth": 0,
    "host_state": 0,
    "icon_image": "",
    "icon_image_alt": "",
    "icon_image_expanded": "",
    "in_check_period": 1,
    "in_notification_period": 1,
    "is_executing": 0,
    "is_flapping": 0,
    "last_check": 1700838450,
    "last_notification": 1696413750,
    "last_state_change": 1696413567,
    "last_state_change_order": 1696413567,
    "last_time_critical": 1700838450,
    "last_time_ok": 1696413267,
    "last_time_unknown": 1694423060,
    "last_time_warning": 0,
    "latency": 0.501,
    "low_flap_threshold": 0,
    "max_check_attempts": 4,
    "modified_attributes_list": [],
    "next_check": 1700838750,
    "notes": "",
    "notes_expanded": "",
    "notes_url": "",
    "notes_url_expanded": "",
    "notification_interval": 0,
    "notification_period": "24x7",
    "notifications_enabled": 1,
    "obsess_over_service": 1,
    "peer_key": "6c09f772ed7c6fb1687621976aef3a2c",
    "peer_name": "bootstack-telefonica-independencia",
    "percent_state_change": 0,
    "perf_data": "",
    "plugin_output": "CRITICAL: nova-compute, brtlvmrs0879co.maas down, Host Aggregate aggregate-zone2 has 1 hosts alive, brtlvmrs0880co.maas down, Host Aggregate aggregate-zone3 has 1 hosts alive",
    "process_performance_data": 1,
    "retry_interval": 1,
    "scheduled_downtime_depth": 0,
    "state": 2,
    "state_order": 4,
    "state_type": 1
    }
    """
    return json.loads(nagios_service)

@pytest.fixture()
def nagios_service_json():
    nagios_service = r"""
    {
    "accept_passive_checks" : 1,
    "active_checks_enabled" : 1,
    "check_command" : "check_nrpe_H_HOSTADDRESS__ccheck_telegraf_http_t10!",
    "check_period" : "24x7",
    "checks_enabled" : 1,
    "contact_groups" : [
    "admins"
    ],
    "contacts" : [
    "pagerduty",
    "root"
    ],
    "current_attempt" : 1,
    "description" : "bootstack-hijk-lmn-etcd-2-telegraf_http",
    "display_name" : "bootstack-hijk-lmn-etcd-2-telegraf_http",
    "event_handler_enabled" : 1,
    "execution_time" : 0.143912,
    "flap_detection_enabled" : 1,
    "has_been_checked" : 1,
    "host_accept_passive_checks" : 1,
    "host_active_checks_enabled" : 1,
    "host_address" : "10.169.129.151",
    "host_alias" : "bootstack-hijk-lmn-etcd-2",
    "host_check_command" : "check-host-alive",
    "host_checks_enabled" : 1,
    "host_current_attempt" : 1,
    "host_display_name" : "bootstack-hijk-lmn-etcd-2",
    "host_groups" : [
    "bootstack-hijk-lmn-etcd",
    "all"
    ],
    "host_has_been_checked" : 1,
    "host_icon_image_alt" : "Ubuntu Linux",
    "host_icon_image_expanded" : "base/ubuntu.png",
    "host_last_state_change" : 1695815622,
    "host_latency" : 0.257,
    "host_name" : "bootstack-hijk-lmn-etcd-2",
    "host_notifications_enabled" : 1,
    "host_parents" : [
    "bootstack-hijk-lmn-vault-2"
    ],
    "host_perf_data" : "rta=0.631000ms;5000.000000;5000.000000;0.000000 pl=0%;100;100;0",
    "host_pl" : "0",
    "host_pl_unit" : "%",
    "host_plugin_output" : "PING OK - Packet loss = 0%, RTA = 0.63 ms",
    "host_rta" : "0.631000",
    "host_rta_unit" : "ms",
    "in_check_period" : 1,
    "in_notification_period" : 1,
    "last_check" : 1699603636,
    "last_state_change" : 1695815754,
    "last_state_change_order" : 1695815754,
    "last_time_ok" : 1699603636,
    "latency" : 0.21,
    "max_check_attempts" : 4,
    "next_check" : 1699603936,
    "notification_period" : "24x7",
    "notifications_enabled" : 1,
    "obsess_over_service" : 1,
    "peer_key" : "0348dcd774a2892097b9d5c84ce882d3",
    "peer_name" : "juju",
    "perf_data" : "time=0.007001s;;;0.000000;10.000000 size=95245B;;;0",
    "plugin_output" : "HTTP OK: HTTP/1.0 200 OK - 95245 bytes in 0.007 second response time",
    "process_performance_data" : 1,
    "size" : "95245",
    "state" : 0,
    "size_unit" : "B",
    "state_type" : 1,
    "time" : "0.007001",
    "time_unit" : "s"
    }
    """
    return json.loads(nagios_service)


def test_nrpedata():
    alert = NRPEData(juju_model="model",
                     alert_identifier="app-unit-0",
                     alert_check_name="check-name",
                     alert_state=0,
                     alert_time=1)

    assert str(NRPEData()) == "::::"
    assert str(alert) == "model:app-unit-0:check-name:0:1"


def test_nrpedata_eq():

    alert1 = NRPEData(juju_model="model",
                      alert_identifier="app-unit-0",
                      alert_check_name="check-name",
                      alert_time=1)

    alert2 = NRPEData(juju_model="model",
                      alert_identifier="app-unit-0",
                      alert_check_name="check-name",
                      alert_time=1)

    alert_set = set()
    alert_set.add(alert1)
    alert_set.add(alert2)

    assert alert1 == alert2
    assert len(alert_set) == 1


def test_nagios_prom_rules(prom_rule_json, nagios_service_json):
    prom_rule = PrometheusRule(prom_rule_json, "bootstack-hijk-lmn")
    nagios_service = NagiosService(nagios_service_json, "bootstack-hijk-lmn")

    assert prom_rule == nagios_service


def test_nagios_prom_alert_rules(prom_alert_rule_json, nagios_alert_service_json):
    prom_rule = PrometheusRule(prom_alert_rule_json, "bootstack-abcd-efgh")
    nagios_service = NagiosService(nagios_alert_service_json, "bootstack-abcd-efgh")

    assert prom_rule == nagios_service
    assert prom_rule.alert_state == nagios_service.alert_state


def test_to_json(prom_rule_json, nagios_service_json):
    prom_rule = PrometheusRule(prom_rule_json, "bootstack-hijk-lmn")
    nagios_service = NagiosService(nagios_service_json, "bootstack-hijk-lmn")

    assert json.loads(prom_rule.to_json())
    assert json.loads(nagios_service.to_json())
