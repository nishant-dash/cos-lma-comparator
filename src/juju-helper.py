#!/usr/bin/python3

import logging
import sys

from juju import jasyncio
from juju.model import Model


async def connect_model_get_config(
        controller_name='foundation-maas',
        model_name='lma-maas',
        user='admin',
        app_name='nrpe',
        config_names=['nagios_host_context']
    ) -> dict:
    '''Connect to a juju controller and model as a user and get charm config
    information from charms that match the app_name regex.

    :param controller_name: name of the juju controller
    :type controller_name: string
    :param model_name: name of the juju model to connect to
    :type model_name: string
    :param user: name of the juju user that the commands are run against
    :type user: string
    :param app_name: name(regex) of the application to filter against
    :type app_name: string
    :param config_name: names of application configs to get
    :type config_name: string
    '''
    # connect to a model
    model = Model()
    await model.connect(f'{controller_name}:{user}/{model_name}')
    
    # collect all nrpe applications
    nrpe_apps = {}
    all_apps = model.applications
    for k,v in all_apps.items():
        if app_name in k:
            config = await v.get_config()
            # create a mapping from app to dictionary of app config name and value
            nrpe_apps[k] = {c: config[c]['value'] for c in config_names}

    # cleanup
    await model.disconnect()
    return nrpe_apps



def main():
    logging.basicConfig(level=logging.INFO)

    # If you want to see everything sent over the wire, set this to DEBUG.
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    # Run the deploy coroutine in an asyncio event loop, using a helper
    # that abstracts loop creation and teardown.
    ret = jasyncio.run(connect_model_get_config('dash3-serverstack', 'nrpe-test'))
    print(ret)

if __name__ == '__main__':
    main()
