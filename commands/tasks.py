import click


@click.group('tasks', help='Get, create, update, delete, and more for tasks')
def tasks():
    pass


@click.command('list', help='List all tasks that ')
def tasks_list():
    pass


tasks.add_command(tasks_list)
