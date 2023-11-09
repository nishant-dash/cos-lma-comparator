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
    :type config_name: list

    :return: a mapping of application name to a dictionary of its config option
    and value
    :rtype: dictionary
    '''
    # connect to a model
    model = Model()
    await model.connect(f'{controller_name}:{user}/{model_name}')

    # collect all applications that match app name wildcard
    nrpe_config_info = {}
    all_apps = model.applications
    for k, v in all_apps.items():
        if app_name in k:
            config = await v.get_config()
            # create a mapping from app to dictionary of app config name and value
            nrpe_config_info[k] = {c: config[c]['value'] for c in config_names}

    # cleanup
    await model.disconnect()
    return nrpe_config_info


async def connect_model_run_command(
    controller_name='foundation-maas',
    model_name='lma-maas',
    user='admin',
    app_name='thruk-agent',
    command='hostname',
    action=False
) -> dict:
    '''Connect to a juju controller and model as a user and get charm config
    information from charms that match the app_name regex.

    :param controller_name: name of the juju controller
    :type controller_name: string
    :param model_name: name of the juju model to connect to
    :type model_name: string
    :param user: name of the juju user that the commands are run against
    :type user: string
    :param app_name: name(NOT regex) of the application to filter against
    :type app_name: string
    :param commands: list of shell commands to run on a unit of the application
    :type commands: list
    :param action: flag to consider command as juju run_action or juju run
    :type action: bool

    :return: output of the command run against a unit of the application specified
    :rtype: string
    '''
    # connect to a model
    model = Model()
    await model.connect(f'{controller_name}:{user}/{model_name}')

    # get application object and pick first unit to run the command
    output = ""
    app = model.applications[app_name]
    unit = app.units[0]
    if action:
        action = await unit.run_action(command)
        action = await action.wait()
        output = action.results
    else:
        action = await unit.run(command)
        output = action.results
        output = output['Stdout']

    # cleanup
    await model.disconnect()
    return output


async def connect_model_get_status(
    controller_name='foundation-maas',
    model_name='lma-maas',
    user='admin'
) -> dict:
    '''Connect to a juju controller and model as a user and get charm config
    information from charms that match the app_name regex.

    :param controller_name: name of the juju controller
    :type controller_name: string
    :param model_name: name of the juju model to connect to
    :type model_name: string
    :param user: name of the juju user that the commands are run against
    :type user: string

    :return: juju status output
    :rtype: string
    '''
    # connect to a model and get status
    model = Model()
    await model.connect(f'{controller_name}:{user}/{model_name}')
    output = await model.get_status()

    # cleanup
    await model.disconnect()
    return output