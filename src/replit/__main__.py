"""CLI for interacting with your Repl's DB. Written as top-level script."""
import json

import click
from replit import db as database
from replit import termutils as term


def info(value: str) -> str:
    """Wrap given string in a blue color for info contexts."""
    return term.brightblue.fg + value + term.reset


def success(value: str) -> str:
    """Wrap given string in a green color for success contexts."""
    return term.brightgreen.fg + value + term.reset


def failure(value: str) -> str:
    """Wrap given string in a red color for failure/warning contexts."""
    return term.brightred.fg + value + term.reset


@click.group()
@click.version_option("0.0.1")
def cli() -> None:
    """CLI for interacting with your Repl's DB."""


@cli.command(name="keys")
@click.argument("file_path", default="db_keys.json")
def list_keys(file_path: str) -> None:
    """Save all keys in the DB to a JSON file."""
    try:
        file = open(file_path, "w+")
    except FileNotFoundError:
        click.echo(failure(f"No such file or directory '{file_path}'"))
    else:
        keys = list(database.keys())
        json.dump(keys, file)

        click.echo(success(f"Ouput successfully dumped to '{file_path}'"))


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
    try:
        database[key] = val
    except Exception as e:
        click.echo(failure(f"Error occured while setting DB[{key}] to '{val}'"))
        click.echo(failure(f"\n{e}"))
    else:
        click.echo(success(f"DB[{key}] was successfully set to '{val}'"))
        click.echo(info(f"Dynamically typed to {type(val)}"))


@cli.command(name="del")
@click.argument("key")
def del_value(key: str) -> None:
    """Delete the key-value pair located at the given key."""
    try:
        val = database[key]
    except KeyError:
        click.echo(failure(f"The key '{key}' was not found in the DB."))
    else:
        click.echo(success(f"The value '{val}' was found at db['{key}']"))
        flag = click.prompt(failure("Confirm delete? (y/n)"))
        flag = str(flag)
        click.echo()

        if flag == "y":
            del database[key]
            click.echo(success(f"db['{key}'] was successfully deleted."))
        else:
            click.echo(info("Delete operation cancelled."))


@cli.command(name="nuke")
def nuke_db() -> None:
    """Wipe ALL key-value pairs in the DB."""
    flag = click.prompt(failure("Are you sure you want to nuke the DB? (y/n)"))
    flag = str(flag)

    if flag == "y":
        flag = click.prompt(failure("Ok, but like, REALLY sure? (y/n)"))
        flag = str(flag)

        if flag == "y":
            click.echo(info("Beginning Nuke operation...\n"))
            keys = list(database.keys())

            for k in keys:
                del database[k]

            click.echo(success("Nuke operation successful."))
        else:
            click.echo(info("Nuke operation cancelled. (close one!)"))
    else:
        click.echo(info("Nuke operation cancelled."))


@cli.command(name="all")
@click.argument("file_path", default="db_all.json")
def list_all(file_path: str) -> None:
    """Write all keys and values in the DB to a JSON file."""
    try:
        file = open(file_path, "w+")
    except FileNotFoundError:
        click.echo(failure(f"No such file or directory '{file_path}'"))
    else:
        keys = list(database.keys())
        binds = dict([(k, database[k]) for k in keys])

        json.dump(binds, file)

        click.echo(success(f"Output successfully dumped to '{file_path}'"))


if __name__ == "__main__":
    cli(prog_name="repldb")
