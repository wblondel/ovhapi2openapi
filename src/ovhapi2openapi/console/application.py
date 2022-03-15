import click


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    """
    Dummy CLI.
    """
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


@cli.command()
def sync():
    """
    Dummy sync command.
    """
    click.echo('Syncing')
