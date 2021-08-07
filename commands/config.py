import click


def value_or_config(value, config_key):
    if value:
        return value
    return config_get(config_key)


@click.group('config', help='Set config values')
def config():
    pass


@click.group('set', help='Set various configuration values')
def config_set():
    pass


@click.group('get', help='Get various configuration values')
def config_get():
    pass


@click.command('team-id', help='Set the default team ID')
def config_set_teamId():
    pass

@click.command('setup',
               help='Quickly have help in setting up your .clickuprc file')
def setup():
    pass


config.add_command(config_set)
config.add_command(config_get)
