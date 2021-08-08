import click
import json
from os.path import expanduser
import os.path

CONFIG_FILE = expanduser('~/.cliclirc')
CONFIG_OPTIONS_TYPE = click.Choice(
    ['space-id', 'team-id', 'workspace-id', 'user', 'api-key'])


def ensure_config_file():
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as file:
            file.write('{}')
        click.echo('Created config file')


def value_or_config(value, config_key):
    if value:
        return value
    return config_get(config_key)


def direct_get(config_key):
    ensure_config_file()
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        return config['api-key']


@click.group('config', help='Set config values')
def config():
    pass


@click.command('set', help='Set various configuration values')
@click.argument('key', type=CONFIG_OPTIONS_TYPE)
@click.argument('value')
def config_set(key, value):
    ensure_config_file()
    with open(CONFIG_FILE, 'r+') as file:
        config = json.load(file)
        config[key] = value
        file.seek(0)
        file.write(json.dumps(config, indent=4, sort_keys=True))
        file.truncate()
    pass


@click.command('get', help='Get various configuration values')
@click.argument('key', type=CONFIG_OPTIONS_TYPE)
def config_get(key):
    ensure_config_file()
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
        if key in config:
            click.echo(config[key])
        else:
            click.echo('No such config key found')


@click.command('show', help='Show the full config file')
def config_show():
    ensure_config_file()
    with open(CONFIG_FILE, 'r') as file:
        click.echo(file.read())


@click.command('setup',
               help='Quickly have help in setting up your .clicli file')
def setup():
    pass


config.add_command(config_set)
config.add_command(config_get)
config.add_command(config_show)
