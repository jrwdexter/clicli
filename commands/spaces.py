import click
import json
from api import make_api_request
from commands.config import value_or_config


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
    team_id = value_or_config(team_id, 'team-id')
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
    team_id = value_or_config(team_id, 'team-id')
    response = make_api_request('space/%s' % space_id)
    if not include_features and 'features' in response:
        del response['features']
    if not include_statuses and 'statuses' in response:
        del response['statuses']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


spaces.add_command(list_spaces)
spaces.add_command(get_space)
