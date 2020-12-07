import json
import click

from replit import db as database

def chunk(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@click.group()
@click.version_option("0.0.1")
def cli():
    """CLI for interacting with your Repl's DB."""


@cli.command(name="keys")
@click.argument("file_path", default="db_keys.json")
def list_keys(file_path: str):
    """Writes all keys in the DB to a JSON file."""

    file = open(file_path, 'w+')
    keys = list(database.keys())
    json.dump(keys, file)

    click.echo(f"Ouput successfully dumped to '{file_path}'")


@cli.command(name="match")
@click.argument("prefix")
def find_matches(prefix: str):
    """Finds keys with a given prefix."""

    matches = list(database.prefix(prefix))

    if matches:
        click.echo(f"Matches found for '{prefix}':\n")
        click.echo('\n'.join(matches))
    else:
        click.echo(f"No matches found for '{prefix}'")


@cli.command(name="set")
@click.argument("key")
@click.argument("val")
def set_value(key: str, val: str):
    """Sets a DB key to a given value. (Dynamically Typed)"""

    val = eval(val, {})
    try:
        database[key] = val
    except:
        click.echo(f"An error occured while setting DB[{key}] to '{val}'")

    click.echo(f"DB[{key}] was successfully set to '{val}'")


@cli.command(name="all")
@click.argument("file_path", default="db_all.json")
def list_all(file_path: str):
    """Writes all keys and values in the DB to a JSON file."""

    file = open(file_path, 'w+')
    keys = list(database.keys())
    binds = dict([(k, database[k]) for k in keys])
    
    json.dump(binds, file)

    click.echo(f"Ouput successfully dumped to '{file_path}'")


if __name__ == "__main__":
    cli(prog_name="db")
