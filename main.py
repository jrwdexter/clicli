import click
from commands import auth, config, folders, lists, spaces, tasks, teams


@click.group(help="""A tool for getting, managing, and updating clickup issues.

        Clickup is organized into Teams -> Spaces -> Folders -> Lists -> Tasks
""")
def cli():
    pass


cli.add_command(auth.auth)
cli.add_command(config.config)
cli.add_command(spaces.spaces)
cli.add_command(teams.teams)
cli.add_command(folders.folders)
cli.add_command(lists.lists)
cli.add_command(tasks.tasks)

if __name__ == '__main__':
    cli(auto_envvar_prefix='CLICKUP')
