import click


@click.group()
@click.option("--debug/--no-debug", default=False)
def cli(debug: bool) -> None:
    """
    Dummy CLI.
    """
    print(type(debug))
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


@cli.command()
def sync() -> None:
    """
    Dummy sync command.
    """
    click.echo("Syncing")
