import subprocess as sp
from uuid import uuid4 as uid
import json
import yaml
import sys


JUJU = "/snap/bin/juju"

# function to query charmhub with juju to get version numbers for apps
def juju_ssh(
    controller_name="foundations-maas",
    model_name="lma-maas",
    user="admin",
    app_name="thruk-agent",
    command="hostname",
    juju_version="2.9"
    ):
    if juju_version.startswith("2"):
        JUJU = "/snap/bin/juju"
    elif juju_version.startswith("3"):
        JUJU = "/snap/bin/juju_31"
    else:
        # log
        print(f"Can not infer or Unknown juju version {juju_version}")
        return

    cmd = [
        JUJU,
        "ssh",
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command
    ]
    print(f"Running {cmd}")
    output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True)
    # juju_info = ""
    # try:
    #     juju_info = json.loads(output.stdout)
    # except json.JSONDecodeError as error:
    #     print(error)
    return output.stdout

def juju_run_action(
    controller_name="foundations-maas",
    model_name="lma-maas",
    user="admin",
    app_name="thruk-agent",
    command=None,
    juju_version="2.9"
    ):
    if juju_version.startswith("2"):
        JUJU = "/snap/bin/juju"
        run_action_cmd = ["run-action", "--wait"]
    elif juju_version.startswith("3"):
        JUJU = "/snap/bin/juju_31"
        run_action_cmd = ["run"]
    else:
        # log
        print(f"Can not infer or Unknown juju version {juju_version}")
        return

    cmd = [JUJU] + run_action_cmd
    cmd += [
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command
    ]
    print(f"Running {cmd}")
    output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL)
    output = output.stdout.decode('utf-8')
    output_yaml = ""
    try:
        output_yaml = yaml.safe_load(output)
    except yaml.YAMLError as error:
        print(error)
        output_yaml = None
    return output_yaml


if __name__ == '__main__':
    nagios_services_json = juju_ssh(app_name='thruk-agent', command='sudo thruk r /services')
    print(json.loads(nagios_services_json))

    traefik_proxied_endpoints_action_raw = juju_run_action(
            controller_name="microk8s-controller",
            model_name="cos",
            app_name='traefik',
            command='show-proxied-endpoints'
    )
    first_key = list(traefik_proxied_endpoints_action_raw.keys())[0]
    traefik_proxied_endpoints_json = json.loads(
        traefik_proxied_endpoints_action_raw[first_key]['results']['proxied-endpoints']
    )
    print(traefik_proxied_endpoints_json)