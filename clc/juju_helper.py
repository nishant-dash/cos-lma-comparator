import yaml
import logging

from subprocess import run, PIPE, DEVNULL

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
        raise Exception(f"Cannot infer or Unknown juju version {juju_version}")

    cmd = [
        JUJU,
        "ssh",
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command
    ]
    logging.info(f"Running {cmd}")
    output = run(cmd, stdout=PIPE, stderr=DEVNULL, text=True)

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
        raise Exception(f"Cannot infer or Unknown juju version {juju_version}")

    cmd = [JUJU] + run_action_cmd
    cmd += [
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command
    ]

    logging.info(f"Running {cmd}")
    output = run(cmd, stdout=PIPE, stderr=DEVNULL)
    output = output.stdout.decode('utf-8')
    output_yaml = ""
    try:
        output_yaml = yaml.safe_load(output)
    except yaml.YAMLError as error:
        logging.error(error)
        output_yaml = None
    return output_yaml


def juju_config(
    controller_name="foundations-maas",
    model_name="lma-maas",
    user="admin",
    app_name="nagios",
    config="",
):
    cmd = [
        JUJU,
        "config",
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}",
        f"{config}",
    ]
    logging.info(f"Retrieve config: {cmd}")
    output = run(cmd, stdout=PIPE, stderr=DEVNULL, text=True)
    return output.stdout.strip()
