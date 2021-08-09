import click
import json
import sys
from api import make_api_request
from commands.config import value_or_config


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def find_folder_by_name(name: str, space_id: int, archived=False):
    response = make_api_request('space/%s/folder?archived=%s' %
                                (space_id, str(archived)))
    for folder in response['folders']:
        if folder['name'] == name:
            return folder


@click.group('folders',
             help='Get, create, update, delete, and more for folders')
def folders():
    pass


@click.command('list', help='List all folders that belong to a space')
@click.option('-s',
              '--space-id',
              help='The ID of the space to return folders for. '
              'Will use config values if not provided.')
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
    space_id = value_or_config(space_id, 'space-id')
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


@click.command('get', help='Get a single folder by ID')
@click.argument('folder-id')
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
def folders_get(folder_id, include_lists, include_list_statuses):
    response = make_api_request('folder/%s' % folder_id)
    if not include_lists and 'lists' in response:
        del response['lists']
    if include_lists and not include_list_statuses:
        for list in response['lists']:
            if 'statuses' in list:
                del list['statuses']
    click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('create', help='Create a new folder within an existing space')
@click.argument('name')
@click.option('-s',
              '--space-id',
              help='The space ID to create the folder under. '
              'If no value is provided, default value from .cliclirc is used.')
def folders_create(space_id, name):
    space_id = value_or_config(space_id, 'space-id')
    body = {'name': name}
    response = make_api_request('space/%s/folder' % space_id,
                                method='POST',
                                body=body)
    click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('rename',
               help='Renames a file by utilizing either the name or id option')
@click.option('-n',
              '--name',
              required=False,
              help='The original name of the folder to rename.',
              prompt=True)
@click.argument('new-name')
@click.option('--id', help='Rename by ID instead of by name', required=False)
@click.option('-s',
              '--space-id',
              help='If a name is specified, '
              'look for folders in the given space. '
              'Defaults to the space ID in the .cliclirc config.')
def folders_rename(name, space_id, id, new_name):
    body = {'name': new_name}
    if not name and not id:
        click.echo(click.style('Error', fg='red') +
                   ': No name or id provided.',
                   err=True)
        return
    if name and id:
        if sys.stdout.isatty():
            click.echo(
                click.style('Warning', fg='orange') +
                ': both name and ID provided. Defaulting to id.')
    if id:
        response = make_api_request('folder/%s' % id, method='PUT', body=body)
    else:
        space_id = value_or_config(space_id, 'space-id')
        folder = find_folder_by_name(name, space_id)
        if folder is not None:
            response = make_api_request('folder/%s' % folder['id'],
                                        method='PUT',
                                        body=body,
                                        verbose=True)
        else:
            click.echo(
                click.style('Error', fg='red') + ': No such folder found')
            return
    click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('remove', help='Delete a folder')
@click.option('-q',
              '--quiet',
              help='Do not prompt prior to deletion.',
              prompt='Are you sure you want to delete the list? '
              'This is not the same as archiving.',
              is_flag=True,
              expose_value=False,
              callback=abort_if_false)
@click.argument('id')
def folders_remove(id):
    response = make_api_request('folder/%s' % id, method='DELETE')
    click.echo(json.dumps(response, indent=4, sort_keys=True))


folders.add_command(folders_list)
folders.add_command(folders_get)
folders.add_command(folders_create)
folders.add_command(folders_rename)
