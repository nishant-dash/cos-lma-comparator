import subprocess as sp
import yaml

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
