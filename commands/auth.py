import click
from os.path import expanduser


@click.group('auth', help='See and manage auth information')
def auth():
    pass


@click.command('set-access-token',
               help='Set your access token. Get it from Clickup.')
@click.argument('access_token')
def set_access_token(access_token):
    with open(expanduser('~/.clickuprc'), 'w') as file:
        file.write(access_token)
    click.echo(click.style('\nSuccessfully saved clickup token\n', fg='green'))


def get_token():
    with open(expanduser('~/.clickuprc')) as file:
        return file.readline()


auth.add_command(set_access_token)
