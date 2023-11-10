import subprocess as sp
from uuid import uuid4 as uid
import json
import yaml
import sys


class jujuCliHelper:
    def __init__(self, juju_version):
        self.juju = "/snap/bin/juju"

    # function to query charmhub with juju to get version numbers for apps
    def juju_ssh(self, controller, model, user, target, command):
        cmd = [
            self.juju, 
            "ssh", 
            "-m", 
            f"{controller}:{user}/{model}", 
            f"{target}/leader", 
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
    
    def juju_run_action(self, controller, model, user, target, action, juju_version):
        if juju_version.startswith("2"):
            run_action_cmd = ["run-action", "--wait"]
        elif juju_version.startswith("3"):
            run_action_cmd = ["run"]
        else:
            # log
            print(f"Can not infer or Unknown juju version {juju_version}")
            return

        cmd = [self.juju] + run_action_cmd
        cmd += [
            "-m", 
            f"{controller}:{user}/{model}", 
            f"{target}/leader", 
            " -- ", 
            command
        ]
        output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL)
        return output.stdout
        