import logging
import json

import grafana_api.model
import grafana_api.datasource

from . import juju_helper
from .display import print_title


def check_loki_hostnames(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
):
    hostname_labels = get_grafana_datasource_resources_label(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
        'hostname',
    )

    juju_machines_raw = juju_helper.juju_machines_and_containers()
    # Strip <controller>:<model> from the result
    juju_machines = set(map(lambda x: x.split(':')[-1], juju_machines_raw))

    extra_machines = sorted(hostname_labels - juju_machines)
    missing_machines = sorted(juju_machines - hostname_labels)
    common_machines = sorted(hostname_labels & juju_machines)

    if missing_machines:
        print_title("Machines missing in Loki")
        for machine in missing_machines:
            [print(m) for m in juju_machines_raw if m.endswith(machine)]

    if extra_machines:
        print_title("Extra machines Loki")
        [print(m) for m in extra_machines]

    print_title("Loki Logs Summary")
    print(f"missing_loki_machines: {len(missing_machines)}")
    print(f"extra_loki_machines: {len(extra_machines)}")
    print(f"common_loki_machines: {len(common_machines)}")


def check_loki_logs_filenames(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    datasource_name='loki',
):
    juju_applications = get_grafana_datasource_resources_label(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
        'juju_application',
    )

    password, host = get_grafana_pass_url(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
    )

    api_model = grafana_api.model.APIModel(
        username='admin',
        password=password,
        host=host,
    )
    api = grafana_api.api.Api(api_model)

    datasources = grafana_api.datasource.Datasource(api_model)
    for ds in datasources.get_all_datasources():
        # Find datasource id matching datasource_name
        if datasource_name in ds['name']:
            datasource = ds["id"]
            break

    responses = []
    for app in juju_applications:
        query = f'api/datasources/{datasource}/resources/series?match[]={{juju_application="{app}"}}'
        responses += api.call_the_api(query)['data']

    from collections import defaultdict
    results = defaultdict(dict)

    for item in responses:
        app = item['juju_application']
        unit = item['juju_unit']
        log = item['filename']
        results[app].setdefault(unit, []).append(log)
        results[app][unit].sort()

    return json.dumps(results)


def get_grafana_datasource_resources_label(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    label='hostname',
    datasource_name='loki',
):
    password, host = get_grafana_pass_url(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
    )

    api_model = grafana_api.model.APIModel(
        username='admin',
        password=password,
        host=host,
    )

    datasources = grafana_api.datasource.Datasource(api_model)

    for ds in datasources.get_all_datasources():
        if datasource_name in ds['name']:
            query = f'api/datasources/{ds["id"]}/resources/label/{label}/values'
            break

    api = grafana_api.api.Api(api_model)
    result = api.call_the_api(query)['data']

    logging.debug(f"{label} labels {result}")
    return set(result)


def get_grafana_pass_url(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
):
    grafana_action_raw = juju_helper.juju_run_action(
        controller_name=juju_cos_controller,
        model_name=juju_cos_model,
        user=juju_cos_user,
        app_name='grafana',
        command='get-admin-password'
    )

    first_key = list(grafana_action_raw.keys())[0]
    results = grafana_action_raw[first_key]['results']

    return (results['admin-password'], results['url'])
