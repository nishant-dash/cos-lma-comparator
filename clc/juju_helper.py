import yaml
import json
import logging
import jq

from subprocess import run, PIPE, DEVNULL


def juju(version="2.9"):
    return "juju"

    if version.startswith("2"):
        return "juju"
    elif version.startswith("3"):
        return "juju_31"
    else:
        raise Exception(f"Cannot infer or Unknown juju version {version}")


# function to query charmhub with juju to get version numbers for apps
def juju_ssh(
    controller_name="foundations-maas",
    model_name="lma-maas",
    user="admin",
    app_name="thruk-agent",
    command="hostname",
    juju_version="2.9"
):
    cmd = [
        juju(juju_version),
        "ssh",
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command
    ]
    logging.info(f"Running {' '.join(cmd)}")
    output = run(cmd, stdout=PIPE, stderr=DEVNULL, text=True)

    if output.returncode > 0:
        juju_controllers_models()
        raise Exception(f"Juju ssh failed! Check juju controllers/models!\n{' '.join(cmd)}")

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
    else:
        raise Exception(f"Cannot infer or Unknown juju version {juju_version}")

    cmd = [juju(juju_version)] + run_action_cmd
    cmd += [
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}/leader",
        command,
    ]

    logging.info(f"Running {' '.join(cmd)}")

    output = run(cmd, stdout=PIPE, stderr=DEVNULL)

    if output.returncode > 0:
        juju_controllers_models()
        raise Exception(f"Juju run-action failed! Check juju controllers/models!\n{' '.join(cmd)}")

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
        juju(),
        "config",
        "-m",
        f"{controller_name}:{user}/{model_name}",
        f"{app_name}",
        f"{config}",
    ]
    logging.info(f"Retrieve config: {' '.join(cmd)}")
    output = run(cmd, stdout=PIPE, stderr=DEVNULL, text=True)

    if output.returncode > 0:
        juju_controllers_models()
        raise Exception(f"Juju config failed! Check juju controllers/models!\n{' '.join(cmd)}")

    return output.stdout.strip()


def juju_controllers_models():
    controllers_raw = run([juju(), "controllers", "--format", "json"],
                          stdout=PIPE, stderr=DEVNULL, text=True)
    controllers_json = json.loads(controllers_raw.stdout.strip())

    print()
    print("Try the following controllers/models")
    for controller in controllers_json['controllers'].keys():
        cmd = [juju(), "models",
               "--format", "json",
               "--controller", controller]
        model_raw = run(cmd, stdout=PIPE, stderr=DEVNULL, text=True)
        model_json = json.loads(model_raw.stdout.strip())

        for model in model_json['models']:
            if 'lma' in model['short-name'] or 'lma' in model['controller-name']:
                print("--juju-lma-model {} --juju-lma-controller {}".
                      format(model['short-name'], model['controller-name']))

            if 'cos' in model['short-name'] or 'cos' in model['controller-name']:
                print("--juju-cos-model {} --juju-cos-controller {}".
                      format(model['short-name'], model['controller-name']))
    print()


def juju_machines():
    controllers_raw = run([juju(), "controllers", "--format", "json"],
                          stdout=PIPE, stderr=DEVNULL, text=True)
    controllers_json = json.loads(controllers_raw.stdout.strip())

    machines = set()

    for controller in controllers_json['controllers'].keys():
        model_raw = run([juju(), "models", "--format", "json",
                         "--controller", controller],
                        stdout=PIPE, stderr=DEVNULL, text=True)
        model_json = json.loads(model_raw.stdout.strip())
        for model in model_json['models']:
            status_raw = run([juju(), "status", "--format", "json",
                              "--model", f"{controller}:{model['short-name']}"],
                             stdout=PIPE, stderr=DEVNULL, text=True)

            status_json = json.loads(status_raw.stdout.strip())

            # import pdb; pdb.set_trace()
            machines.update(
                jq.compile('.machines[] | select(has("hostname")) | .hostname') \
                .input(status_json) \
                .all()
            )

            machines.update(
                jq.compile('.machines[] | select(has("containers") and (.containers | length > 0)) | .containers[].hostname') \
                .input(status_json) \
                .all()
            )

    return machines