import click
from commands.config import config_get, config_set


@click.group('auth', help='See and manage auth information')
def auth():
    pass


@click.command('set-access-token',
               help='Set your access token within the .cliclirc file.')
@click.argument('access_token')
def set_access_token(access_token):
    config_set('api-key', access_token)


@click.command('get-access-token',
               help='Get your access token from the .cliclirc file.')
def get_token():
    config_get(["api-key"])


auth.add_command(set_access_token)
auth.add_command(get_token)
