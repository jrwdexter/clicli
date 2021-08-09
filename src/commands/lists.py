import click
import sys
import json
from api import make_api_request
from commands.config import value_or_config

CLICKUP_PRIORITIES = click.Choice(['1', '2', '3', '4'])


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def find_list_by_name(name: str,
                      space_id: int = None,
                      folder_id: int = None,
                      archived=False):
    if folder_id:
        response = make_api_request('folder/%s/list?archived=%s' %
                                    (folder_id, str(archived)))
        for list in response['lists']:
            if list['name'] == name:
                return list
    else:
        response = make_api_request('space/%s/list?archived=%s' %
                                    (space_id, str(archived)))
        for list in response['lists']:
            if list['name'] == name:
                return list


@click.group('lists', help='Get, create, update, delete, and more for lists')
def lists():
    pass


@click.command(
    'create',
    help='Create a new list in a specific folder or space. '
    'If you specify --folder-id, the list will be created within a folder. '
    'Otherwise, it is contained within the space '
    'specified or default in config file')
@click.argument('name')
@click.argument('content', required=False)
@click.option('-f',
              '--folder-id',
              help='The folder to create the list within.')
@click.option('-s',
              '--space-id',
              help='Create a folderless list within a space.')
@click.option(
    '-p',
    '--priority',
    help='The priority of the list: 1: Urgent, 2: High, 3: Medium, 4: Low',
    type=CLICKUP_PRIORITIES)
@click.option('-a', '--assignee', help='Assign the list to a specific user.')
@click.option('-d', '--due-date', help='Specify a due date for the the list')
@click.option('-t',
              '--due-date-time',
              help='Specify a due date time for the the list')
@click.option('-s', '--status', help='Specify a status for the list')
def lists_create(name, folder_id, space_id, priority, assignee, content,
                 due_date, due_date_time, status):
    real_space_id = value_or_config(space_id, 'space-id', silent=True)
    real_folder_id = value_or_config(folder_id, 'folder-id', silent=True)
    body = {
        'name': name,
        'content': content,
        'due_date': due_date,
        'due_date_time': due_date_time,
        'priority': priority,
        'assignee': assignee,
        'status': status,
    }
    if not real_folder_id and not real_space_id:
        click.echo(
            click.style('Error', fg='red') +
            ': provide either --space-id or --folder-id.')
        return
    if space_id and folder_id:
        if sys.stdout.isatty():
            click.echo(
                click.style('Warning', fg='orange') +
                ': both --space-id and --folder-id provided.' +
                'Defaulting to --folder-id value.')
    if folder_id or (real_folder_id and not space_id):
        response = make_api_request('folder/%s/list' % real_folder_id,
                                    method='POST',
                                    body=body)
        click.echo(json.dumps(response, indent=4, sort_keys=True))
    else:
        response = make_api_request('space/%s/list' % real_space_id,
                                    method='POST',
                                    body=body)
        click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command(
    'list',
    help='List all lists that belong to a specific folder or space.'
    'If you specify a folder ID, folderless lists will not be included.')
@click.option('-s',
              '--space-id',
              help='The space to find folderless lists within.')
@click.option('-f', '--folder-id', help='The folder to find lists within.')
@click.option('-a',
              '--archived',
              help='Include archived spaces',
              is_flag=True,
              default=False,
              required=False)
@click.option('--me',
              help='Return lists assigned to me. '
              'Your user is defined by ' +
              click.style('config set user', fg='green') + '.',
              is_flag=True,
              default=False,
              required=False)
@click.option('-u', '--user', help='Return lists assigned to the given user.')
def lists_list(space_id, folder_id, archived, me, user):
    real_space_id = value_or_config(space_id, 'space-id', silent=True)
    real_folder_id = value_or_config(folder_id, 'folder-id', silent=True)
    user = value_or_config(user, 'user')
    if not real_folder_id and not real_space_id:
        click.echo(
            click.style('Error', fg='red') +
            ': provide either --space-id or --folder-id.')
        return
    if space_id and folder_id:
        if sys.stdout.isatty():
            click.echo(
                click.style('Warning', fg='orange') +
                ': both --space-id and --folder-id provided.' +
                'Defaulting to --folder-id value.')
    if folder_id or (real_folder_id and not space_id):
        response = make_api_request('folder/%s/list?archived=%s' %
                                    (real_folder_id, str(archived)))
        if user or me:
            lists = [
                list for list in response['lists'] if list['assignee'] == user
            ]
            response['lists'] = lists
        click.echo(json.dumps(response, indent=4, sort_keys=True))
    else:
        response = make_api_request('space/%s/list?archived=%s' %
                                    (real_space_id, str(archived)))
        if user or me:
            lists = [
                list for list in response['lists'] if list['assignee'] == user
            ]
            response['lists'] = lists
        click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('remove', help='Delete a list')
@click.option('-q',
              '--quiet',
              help='Do not prompt prior to deletion.',
              prompt='Are you sure you want to delete the list? '
              'This is not the same as archiving.',
              is_flag=True,
              expose_value=False,
              callback=abort_if_false)
@click.argument('id')
def lists_remove(id):
    response = make_api_request('list/%s' % id, method='DELETE')
    click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('get', help='Get a list')
@click.argument('id_or_name')
@click.option('-f',
              '--folder-id',
              help='ID of the folder to get the list from.')
@click.option('-s',
              '--space-id',
              help='ID of the space to get the folderless list from')
def lists_get(id_or_name: str, space_id, folder_id):
    if id_or_name.isnumeric():
        response = make_api_request('list/%s' % id_or_name)
        click.echo(json.dumps(response, indent=4, sort_keys=True))
    else:
        space_id = value_or_config(space_id, 'space-id', silent=True)
        folder_id = value_or_config(folder_id, 'folder-id', silent=True)
        click.echo(id_or_name)
        small_response = find_list_by_name(id_or_name,
                                           space_id=space_id,
                                           folder_id=folder_id)
        response = make_api_request('list/%s' % small_response['id'])
        click.echo(json.dumps(response, indent=4, sort_keys=True))


@click.command('update',
               help='Renames a file by utilizing either the name or id option')
@click.option('-n',
              '--name',
              required=False,
              help='The original name of the list to rename.',
              prompt=True)
@click.argument('new-name')
@click.option('-c', '--content', help='The content (string) of the list')
@click.option('--id', help='Rename by ID instead of by name', required=False)
@click.option('-s',
              '--space-id',
              help='If a name is specified, '
              'look for lists in the given space. '
              'Defaults to the space ID in the .cliclirc config.')
@click.option('-f',
              '--folder-id',
              help='If a name is specified, '
              'look for lists in the given folder. '
              'Defaults to the folder ID in the .cliclirc config.')
@click.option(
    '-p',
    '--priority',
    help='The priority of the list: 1: Urgent, 2: High, 3: Medium, 4: Low',
    type=CLICKUP_PRIORITIES)
@click.option('-a', '--assignee', help='Assign the list to a specific user.')
@click.option('-d', '--due-date', help='Specify a due date for the the list')
@click.option('-t',
              '--due-date-time',
              help='Specify a due date time for the the list')
@click.option('-s', '--status', help='Specify a status for the list')
@click.option('--unset-status', help='Remove the status of the list')
def lists_update(name, space_id, folder_id, id, new_name, priority, assignee,
                 due_date, due_date_time, status, unset_status, content):
    body = {
        'name': new_name,
        'content': content,
        'due_date': due_date,
        'due_date_time': due_date_time,
        'priority': priority,
        'assignee': assignee,
        'status': status,
        'unset_status': unset_status,
    }
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
        response = make_api_request('list/%s' % id, method='PUT', body=body)
    else:
        real_space_id = value_or_config(space_id, 'space-id')
        real_folder_id = value_or_config(space_id, 'folder_id')
        if folder_id or real_folder_id and not space_id:
            # We are going to find the list within a folder
            list = find_list_by_name(name, folder_id=real_folder_id)
            if list is not None:
                response = make_api_request('list/%s' % list['id'],
                                            method='PUT',
                                            body=body,
                                            verbose=True)
            else:
                click.echo(
                    click.style('Error', fg='red') + ': No such list found')
                return
        else:
            # We are going to find the list within a folder
            list = find_list_by_name(name, space_id=real_space_id)
            if list is not None:
                response = make_api_request('list/%s' % list['id'],
                                            method='PUT',
                                            body=body,
                                            verbose=True)
            else:
                click.echo(
                    click.style('Error', fg='red') + ': No such list found')
                return
    click.echo(json.dumps(response, indent=4, sort_keys=True))


lists.add_command(lists_list)
lists.add_command(lists_create)
lists.add_command(lists_remove)
lists.add_command(lists_get)
lists.add_command(lists_update)
