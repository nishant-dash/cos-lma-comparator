import json
import pytest

from clc.prometheus import PrometheusRule, PrometheusRules


@pytest.fixture
def prometheus_rules_json():
    with open("tests/test_data/prometheus.json") as f:
        return json.load(f)


def test_prometheus_rule(prometheus_rules_json):
    rule = PrometheusRule(prometheus_rules_json["data"]["groups"][200]["rules"][0])
    assert rule.juju_unit == "nrpe-storage/0"
    assert rule.alert_check_name == "check_ipmi"


def test_prometheus(prometheus_rules_json):
    assert PrometheusRules(prometheus_rules_json)
