"""CLI for interacting with your Repl's DB. Written as top-level script."""
import json

import click
from replit import db as database


reset = "\u001b[0m"


def info(value: str) -> str:
    """Wrap given string in a blue color for info contexts."""
    # Bright blue foreground
    return "\u001b[34;1m" + value + reset


def success(value: str) -> str:
    """Wrap given string in a green color for success contexts."""
    # Bright green foreground
    return "\u001b[32;1m" + value + reset


def failure(value: str) -> str:
    """Wrap given string in a red color for failure/warning contexts."""
    # Bright red foreground
    return "\u001b[31;1m" + value + reset


@click.group()
@click.version_option("0.0.1")
def cli() -> None:
    """CLI for interacting with your Repl's DB."""


@cli.command(name="match")
@click.argument("prefix")
def find_matches(prefix: str) -> None:
    """List all keys that match the given prefix."""
    matches = list(database.prefix(prefix))

    if matches:
        click.echo(success(f"Matches found for '{prefix}':\n"))
        click.echo("\n".join(matches))
    else:
        click.echo(failure(f"No matches found for '{prefix}'"))


@cli.command(name="set")
@click.argument("key")
@click.argument("val")
def set_value(key: str, val: str) -> None:
    """Add a given key-value pair to the DB."""
    database[key] = val
    click.echo(success(f"DB[{key}] was successfully set to '{val}'"))


@cli.command(name="del")
@click.argument("key")
def del_value(key: str) -> None:
    """Delete the key-value pair located at the given key."""
    try:
        del database[key]
    except KeyError:
        click.echo(failure(f"The key '{key}' was not found in the DB."))
    else:
        del database[key]
        click.echo(success(f"db['{key}'] was successfully deleted."))


@cli.command(name="nuke")
@click.option("--i-am-sure", is_flag=True)
def nuke_db(i_am_sure: bool) -> None:
    """Wipe ALL key-value pairs in the DB."""
    if i_am_sure:
        click.echo(info("Beginning Nuke operation...\n"))
        keys = list(database.keys())

        for k in keys:
            del database[k]

        click.echo(success("Nuke operation successful."))
    else:
        click.echo(
            failure(
                "If you REALLY want to delete everything in your database, "
                "run again with the --i-am-sure flag."
            )
        )


@cli.command(name="dump")
@click.argument("file_path")
def list_all(file_path: str) -> None:
    """Write all keys and values in the DB to a JSON file."""
    with open(file_path, "w") as f:
        keys = list(database.keys())
        binds = dict([(k, json.loads(database.get_raw(k))) for k in keys])

        json.dump(binds, f)

        click.echo(success(f"Output successfully dumped to '{file_path}'"))


if __name__ == "__main__":
    cli(prog_name="repldb")
