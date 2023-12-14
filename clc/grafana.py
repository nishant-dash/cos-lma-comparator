import logging

import grafana_api.model
import grafana_api.datasource

from . import juju_helper
from .display import print_title


def check_loki_hostnames(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
):
    resources = get_grafana_datasource_resources(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
    )
    hostname_labels = set([r['hostname'] for r in resources if 'hostname' in r])

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


def get_loki_logs_filenames(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    datasource_name='loki',
):
    resources = get_grafana_datasource_resources(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
    )
    from collections import defaultdict
    results = defaultdict(dict)

    for item in resources:
        app = item.get('juju_application', '_')
        unit = item.get('juju_unit', '_')
        log = item.get('filename', '_')
        results[app].setdefault(unit, []).append(log)
        results[app][unit].sort()

    return results


def get_grafana_datasource_resources(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
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
        timeout=300,
    )

    datasources = grafana_api.datasource.Datasource(api_model)

    for ds in datasources.get_all_datasources():
        if datasource_name in ds['name']:
            query = f'api/datasources/{ds["id"]}/resources/series?match[]={{}}'
            break

    api = grafana_api.api.Api(api_model)
    result = api.call_the_api(query)['data']

    logging.debug(f"Resources {result}")
    return result


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
