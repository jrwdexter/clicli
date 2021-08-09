import click
import json
from datetime import datetime
from api import make_api_request
from commands.config import direct_get
from urllib import parse

CLICKUP_ORDER = click.Choice(['id', 'created', 'updated', 'due_date'])


@click.group('tasks', help='Get, create, update, delete, and more for tasks')
def tasks():
    pass


@click.command('list', help='List all tasks from a list')
@click.argument('list_id', type=int)
@click.option('--page',
              help='Page of tasks',
              required=False,
              default=0,
              type=int)
@click.option('--all',
              is_flag=True,
              help='Automatically paginate through all pages '
              '(will make multiple requests)')
@click.option('-a',
              '--archived',
              is_flag=True,
              help='Include archived results in the page')
@click.option('-o',
              '--order',
              help='Order by the given property',
              type=CLICKUP_ORDER)
@click.option('-r',
              '--reverse',
              is_flag=True,
              help='Reverse the order of the results')
@click.option('--subtasks', is_flag=True, help='Include subtasks')
@click.option('-s',
              '--statuses',
              help='Statuses to query. '
              'Comma seperated lists of statuses to include')
@click.option('--include-closed',
              is_flag=True,
              help='Include closed tasks in results. '
              'Cannot be combined with --status flag.')
@click.option('--assignees',
              help='Assignees to query for. '
              'Comma seperated lists of assignees to include.')
@click.option('--me', is_flag=True, help='Query for tasks assigned to me.')
@click.option('--due-date-gt',
              help='Query for tasks that have a due date '
              'greater than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--due-date-lt',
              help='Query for tasks that have a due date '
              'less than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--date-created-gt',
              help='Query for tasks that have a created date '
              'greater than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--date-created-lt',
              help='Query for tasks that have a created date '
              'less than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--date-updated-gt',
              help='Query for tasks that have a updated date '
              'greater than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--date-updated-lt',
              help='Query for tasks that have a updated date '
              'less than the one given',
              type=click.DateTime(formats=['%Y-%m-%d']))
# TODO: Include flags to cut out list, project, folder, space info
# (eg. --include-list)
# TODO: Add flag for opening the tasks with prompting (--open or --web)
def tasks_list(list_id, page, all, order, archived, reverse, subtasks,
               statuses: str, include_closed, assignees, me,
               due_date_gt: datetime, due_date_lt: datetime,
               date_created_gt: datetime, date_created_lt: datetime,
               date_updated_gt: datetime, date_updated_lt: datetime):
    # TODO: Need to resolve lookup of emails to user IDs (users module)
    if me:
        me_user = direct_get('user')
        if assignees:
            assignees += ',%s' % me_user
        else:
            assignees = me_user

    query_parameters = {
        'archived':
        str(archived).lower(),
        'order_by':
        order,
        'reverse':
        str(reverse).lower(),
        'subtasks':
        str(subtasks).lower(),
        'statuses[]':
        statuses if statuses else None,
        'include_closed':
        str(include_closed).lower(),
        'assignees[]':
        str(assignees.split(',')) if assignees else None,
        'due_date_gt':
        int(due_date_gt.timestamp()) if due_date_gt else None,
        'due_date_lt':
        int(due_date_lt.timestamp()) if due_date_lt else None,
        'date_created_gt':
        int(date_created_gt.timestamp()) if date_created_gt else None,
        'date_created_lt':
        int(date_created_lt.timestamp()) if date_created_lt else None,
        'date_updated_gt':
        int(date_updated_gt.timestamp()) if date_updated_gt else None,
        'date_updated_lt':
        int(date_updated_lt.timestamp()) if date_updated_lt else None
    }
    # Remove None and falsy values to clean up string
    for (key, value) in dict(query_parameters).items():
        if (value is None) or (value == 'false'):
            del query_parameters[key]
    query_str = parse.urlencode(query_parameters)

    if all:
        # If we are getting all elements, let's do pagination
        full_response = {'tasks': []}
        while len(full_response['tasks']) == page * 100:
            response = make_api_request('list/%s/task?page=%s&%s' %
                                        (list_id, page, query_str))
            full_response['tasks'] = full_response['tasks'] + response['tasks']
            page += 1
        response = full_response
    else:
        response = make_api_request('list/%s/task?page=%s&%s' %
                                    (list_id, page, query_str))

        if (len(response['tasks']) == 100 or page != 0):
            response['page'] = page

    click.echo(json.dumps(response, indent=4))


tasks.add_command(tasks_list)
