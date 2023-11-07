#!/usr/bin/python3

import logging
import sys

from juju import jasyncio
from juju.model import Model


async def connect_model(
        controller_name='foundation-maas',
        model_name='lma-maas',
        user='admin'
    ):
    # connect to a model
    model = Model()
    await model.connect(f'{controller_name}:{user}/{model_name}')
    
    # collect all nrpe applications
    nrpe_apps = {}
    all_apps = model.applications
    for k,v in all_apps.items():
        if "nrpe" in k:
            config = await v.get_config()
            nrpe_apps[k] = config['nagios_host_context']['value']

    # cleanup
    await model.disconnect()
    print(nrpe_apps)



def main():
    logging.basicConfig(level=logging.INFO)

    # If you want to see everything sent over the wire, set this to DEBUG.
    ws_logger = logging.getLogger('websockets.protocol')
    ws_logger.setLevel(logging.INFO)

    # Run the deploy coroutine in an asyncio event loop, using a helper
    # that abstracts loop creation and teardown.
    jasyncio.run(connect_model('dash3-serverstack', 'nrpe-test'))


if __name__ == '__main__':
    main()
