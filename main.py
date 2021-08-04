import click
import http.client
import json
from os.path import expanduser
import sys
import urllib

HOST = 'api.clickup.com'
BASE_PATH = '/api/v2/'


def value_or_config(value, config_key):
    if value:
        return value
    return config_get(config_key)


def make_api_request(path):
    connection = http.client.HTTPSConnection(HOST)
    headers = {'Authorization': get_token()}
    url = urllib.parse.urljoin(BASE_PATH, path)
    if sys.stdout.isatty():
        click.echo(click.style(url, fg='blue'))
    connection.request('GET', url, headers=headers)
    response = connection.getresponse()
    response_body = response.read().decode()
    response_json = json.loads(response_body)
    return response_json


@click.group(help="""A tool for getting, managing, and updating clickup issues.

        Clickup is organized into Teams -> Spaces -> Folders -> Lists -> Tasks
""")
def cli():
    pass


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


@click.group(
    'teams',
    help='Get teams you are a part of. In the UI, this is called "Workspaces"'
)  # noqa: W291
def teams():
    pass


@click.command('list', help='List all teams you have access to')
@click.option('--include-members',
              help='True to include member information',
              default=False,
              is_flag=True)
@click.option('--include-roles',
              help='True to include role information',
              default=False,
              is_flag=True)
def list_teams(include_members, include_roles):
    response = make_api_request('team')
    if 'teams' in response:
        for team in response['teams']:
            if not include_members and 'members' in team:
                del team['members']
            if not include_roles and 'roles' in team:
                del team['roles']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


teams.add_command(list_teams)


@click.group('spaces', help='List, view, update, and delete spaces')
def spaces():
    pass


@click.command('list', help='List all spaces you have access to')
@click.option('-t',
              '--team-id',
              help='The team ID you want to access',
              required=False)
@click.option('-a',
              '--archived',
              help='Include archived spaces',
              is_flag=True,
              default=False,
              required=False)
@click.option('--include-features',
              help='Include feature information',
              is_flag=True,
              default=False,
              required=False)
@click.option('--include-statuses',
              help='Include any custom status information',
              is_flag=True,
              default=False,
              required=False)
def list_spaces(team_id, archived, include_features, include_statuses):
    response = make_api_request('team/%s/space?archived=%s' %
                                (team_id, str(archived)))
    if 'spaces' in response:
        for space in response['spaces']:
            if not include_features and 'features' in space:
                del space['features']
            if not include_statuses and 'statuses' in space:
                del space['statuses']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('get', help='Get a single space and associated information')
@click.option('-s', '--space-id', help='The ID of the space to return')
@click.option('--include-features',
              help='Include feature information',
              is_flag=True,
              default=False,
              required=False)
@click.option('--include-statuses',
              help='Include any custom status information',
              is_flag=True,
              default=False,
              required=False)
def get_space(space_id, include_features, include_statuses):
    response = make_api_request('space/%s' % space_id)
    if not include_features and 'features' in response:
        del response['features']
    if not include_statuses and 'statuses' in response:
        del response['statuses']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


spaces.add_command(list_spaces)
spaces.add_command(get_space)


@click.group('folders',
             help='Get, create, update, delete, and more for folders')
def folders():
    pass


@click.command('list', help='List all folders that ')
@click.option('-s', '--space-id', help='The ID of the space to return')
@click.option('-a',
              '--archived',
              help='Include archived spaces',
              is_flag=True,
              default=False,
              required=False)
@click.option('--include-lists',
              help='Include feature information',
              is_flag=True,
              default=False,
              required=False)
@click.option('--include-list-statuses',
              help='Include feature information',
              is_flag=True,
              default=False,
              required=False)
def folders_list(space_id, archived, include_lists, include_list_statuses):
    response = make_api_request('space/%s/folder?archived=%s' %
                                (space_id, str(archived)))
    if 'folders' in response:
        for folder in response['folders']:
            if not include_lists and 'lists' in folder:
                del folder['lists']
            if include_lists and not include_list_statuses:
                for list in folder['lists']:
                    if 'statuses' in list:
                        del list['statuses']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


folders.add_command(folders_list)


@click.group('lists', help='Get, create, update, delete, and more for lists')
def lists():
    pass


@click.command('list', help='List all lists that ')
def lists_list():
    pass


lists.add_command(lists_list)


@click.group('tasks', help='Get, create, update, delete, and more for tasks')
def tasks():
    pass


@click.command('list', help='List all tasks that ')
def tasks_list():
    pass


tasks.add_command(tasks_list)


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


config.add_command(config_set)
config.add_command(config_get)


@click.command('setup',
               help='Quickly have help in setting up your .clickuprc file')
def setup():
    pass


cli.add_command(auth)
cli.add_command(config)
cli.add_command(spaces)
cli.add_command(teams)
cli.add_command(folders)
cli.add_command(lists)
cli.add_command(tasks)

if __name__ == '__main__':
    cli(auto_envvar_prefix='CLICKUP')
