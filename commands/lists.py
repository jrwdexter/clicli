import click


@click.group('lists', help='Get, create, update, delete, and more for lists')
def lists():
    pass


@click.command('list', help='List all lists that ')
def lists_list():
    pass


lists.add_command(lists_list)
