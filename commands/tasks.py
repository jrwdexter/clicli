import click
import json
from api import make_api_request


@click.group('tasks', help='Get, create, update, delete, and more for tasks')
def tasks():
    pass


@click.command('list', help='List all tasks from a list')
@click.option('-l',
              '--list-id',
              help='List ID',
              required=True,
              type=int)
@click.option('--page',
              help='Page of tasks',
              required=False,
              default=0,
              type=int)
def tasks_list(list_id, page):
    response = make_api_request('list/%s/task?page=%s' %
                        (list_id, page))

    if (len(response['tasks']) == 100 or page != 0):
        response['page'] = page

    click.echo(json.dumps(response, indent=4, sort_keys=True))


tasks.add_command(tasks_list)
