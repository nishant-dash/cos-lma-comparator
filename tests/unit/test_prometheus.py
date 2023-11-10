import json
import pytest

from clc.prometheus import PrometheusRule, PrometheusRules


@pytest.fixture
def prometheus_rules_json():
    with open("tests/test_data/prometheus.json") as f:
        return json.load(f)


def test_prometheus_rule(prometheus_rules_json):
    rule = prometheus_rules_json["data"]["groups"][0]["rules"][0]
    assert PrometheusRule(rule)


def test_prometheus(prometheus_rules_json):
    assert PrometheusRules(prometheus_rules_json)
