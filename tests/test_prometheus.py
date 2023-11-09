import json
import pytest

from clc.prometheus import PrometheusRule, PrometheusRules


@pytest.fixture
def prometheus_rules_json():
    with open("test_data/prometheus.json") as f:
        return json.load(f)


def nagios_services_json():
    with open("test_data/thruk-agent.services.json") as f:
        return json.load(f)


def test_prometheus(prometheus_rules_json):
    prometheus_rules = PrometheusRules(prometheus_rules_json)
    assert len(prometheus_rules.alerts()) > 0, "prometheus alerts are empty"
    assert prometheus_rules[0] is PrometheusRule
