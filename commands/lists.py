import click
import sys
import json
from api import make_api_request
from commands.config import value_or_config

CLICKUP_PRIORITIES = click.Choice([1, 2, 3, 4])


@click.group('lists', help='Get, create, update, delete, and more for lists')
def lists():
    pass


@click.command(
    'create',
    help='Create a new list in a specific folder or space.'
    'If you specify --folder-id, the list will be created within a folder.'
    'Otherwise, it is contained within the space')
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
def lists_list(space_id, folder_id, archived):
    real_space_id = value_or_config(space_id, 'space-id', silent=True)
    real_folder_id = value_or_config(folder_id, 'folder-id', silent=True)
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
        click.echo(json.dumps(response, indent=4, sort_keys=True))
    else:
        response = make_api_request('space/%s/list?archived=%s' %
                                    (real_space_id, str(archived)))
        click.echo(json.dumps(response, indent=4, sort_keys=True))


lists.add_command(lists_list)
lists.add_command(lists_create)
