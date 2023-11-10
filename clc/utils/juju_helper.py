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
        " -- ", 
        command
    ]
    output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL)
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
        run_action_cmd = ["run-action", "--wait"]
    elif juju_version.startswith("3"):
        run_action_cmd = ["run"]
        JUJU = "/snap/bin/juju_31"
    else:
        # log
        print(f"Can not infer or Unknown juju version {juju_version}")
        return

    cmd = [JUJU] + run_action_cmd
    cmd += [
        "-m", 
        f"{controller_name}:{user}/{model_name}", 
        f"{app_name}/leader", 
        " -- ", 
        command
    ]
    output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL)
    return output.stdout
        