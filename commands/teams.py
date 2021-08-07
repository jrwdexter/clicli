import click


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
