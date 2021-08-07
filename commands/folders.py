import click
import json
from api import make_api_request


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
