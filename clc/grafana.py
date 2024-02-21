import logging
import json

import grafana_api.model
import grafana_api.datasource

from . import juju_helper
from .display import print_title


def check_loki_units(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    insecure,
):
    resources = get_grafana_datasource_resources(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
        insecure,
    )
    instance_labels = set([r['instance'].split('_')[-1] for r in resources if 'instance' in r])

    juju_units_raw = juju_helper.juju_units()
    juju_units = set(map(lambda x: x.split(':')[-1], juju_units_raw))

    extra_units = sorted(instance_labels - juju_units)
    missing_units = sorted(juju_units - instance_labels)
    common_units = sorted(instance_labels & juju_units)

    if missing_units:
        print_title("Units missing in Loki")
        for unit in missing_units:
            [print(u) for u in juju_units_raw if u.endswith(unit)]

    if extra_units:
        print_title("Extra units Loki")
        [print(u) for u in extra_units]

    print_title("Loki Logs Summary")
    print(f"missing_loki_units: {len(missing_units)}")
    print(f"extra_loki_units: {len(extra_units)}")
    print(f"common_loki_units: {len(common_units)}")


def check_loki_hostnames(
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    insecure,
):
    resources = get_grafana_datasource_resources(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
        insecure,
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
    insecure,
    datasource_name='loki',
):
    resources = get_grafana_datasource_resources(
        juju_cos_controller,
        juju_cos_model,
        juju_cos_user,
        insecure,
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
    insecure,
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

    if insecure:
        api_model.ssl_context=False

    datasources = grafana_api.datasource.Datasource(api_model)

    for ds in datasources.get_all_datasources():
        if datasource_name in ds['name']:
            query = f'api/datasources/{ds["id"]}/resources/series?match[]={{}}&start=1705079825534000000&end=1705083425534000000'
            break

    api = grafana_api.api.Api(api_model)
    result = api.call_the_api(query)['data']

    logging.debug(f"Resources {json.dumps(result)}")
    return result


def get_grafana_pass_url(
    juju_controller,
    juju_model,
    juju_user,
):
    if 'cos' in juju_model:
        _command = 'get-admin-password'
        _password = 'admin-password'
    else:
        _command = 'get-login-info'
        _password = 'password'

    grafana_action_raw = juju_helper.juju_run_action(
        controller_name=juju_controller,
        model_name=juju_model,
        user=juju_user,
        app_name='grafana',
        command=_command,
    )

    first_key = list(grafana_action_raw.keys())[0]
    results = grafana_action_raw[first_key]['results']

    return (results[_password], results['url'])

def check_grafana_dashboards(
    juju_lma_controller,
    juju_lma_model,
    juju_lma_user,
    juju_cos_controller,
    juju_cos_model,
    juju_cos_user,
    insecure,
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

    if insecure:
        api_model.ssl_context=False

