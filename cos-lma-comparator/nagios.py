import juju_helper

from juju import jasyncio


def get_nagios_data(args):
    nagios_services_json = jasyncio.run(
        juju_helper.connect_model_run_command(
            controller_name=args.juju_controller,
            model_name=args.juju_model,
            user=args.juju_user,
            app_name='thruk-agent',
            command='thruk r /services',
        )
    )
    return nagios_services_json
