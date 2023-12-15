import json
import pytest

from clc.prometheus import PrometheusRule, PrometheusRules


@pytest.fixture
def prometheus_rules_json():
    with open("tests/test_data/prometheus.json") as f:
        return json.load(f)


def test_prometheus_rule(prometheus_rules_json):
    rule = PrometheusRule(
        prometheus_rules_json["data"]["groups"][200]["rules"][0],
        "bootstack-hijk-lmn-opqrst")
    assert rule.alert_identifier == "bootstack-hijk-lmn-opqrst-storage-6"
    assert rule.alert_check_name == "ipmi"
    assert rule.juju_unit == "storage/6"


def test_prometheus(prometheus_rules_json):
    assert PrometheusRules(prometheus_rules_json, "bootstack-hijk-lmn-opqrst")


def test_prometheus_rule_alert_infinite(prometheus_rules_json):
    rule_json = prometheus_rules_json["data"]["groups"][200]["rules"][0]
    rule_json['alerts'] = [{'value': "+Inf"}]
    rule = PrometheusRule(rule_json, "bootstack-hijk-lmn-opqrst")
    assert rule.alert_state == -1
