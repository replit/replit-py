import os
import json
import click

import replit.termutils as term
from replit import db as database


def wrap(color: term.Color, value: str):
    return color.fg + value + term.reset


def info(value: str):
    return term.brightblue.fg + value + term.reset


def success(value: str):
    return term.brightgreen.fg + value + term.reset


def failure(value: str):
    return term.brightred.fg + value + term.reset


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

    try:
        file = open(file_path, 'w+')
    except:
        click.echo(failure(f"No such file or directory '{file_path}'"))
    else:
        keys = list(database.keys())
        json.dump(keys, file)

        click.echo(success(f"Ouput successfully dumped to '{file_path}'"))


@cli.command(name="match")
@click.argument("prefix")
def find_matches(prefix: str):
    """Finds keys with a given prefix."""

    matches = list(database.prefix(prefix))

    if matches:
        click.echo(success(f"Matches found for '{prefix}':\n"))
        click.echo('\n'.join(matches))
    else:
        click.echo(failure(f"No matches found for '{prefix}'"))


@cli.command(name="set")
@click.argument("key")
@click.argument("val")
def set_value(key: str, val: str):
    """Sets a DB key to a given value. (Dynamically Typed)"""
        
    try:
        val = eval(val, {})
        database[key] = val
    except:
        click.echo(failure(f"An error occured while setting DB[{key}] to '{val}'"))
    else:
        click.echo(success(f"DB[{key}] was successfully set to '{val}'"))
        click.echo(info(f"Dynamically typed to {type(val)}"))


@cli.command(name="del")
@click.argument("key")
def del_value(key: str):
    """Deletes the key-value pair of the given key."""

    try:
        val = database[key]
    except KeyError:
        click.echo(failure(f"The key '{key}' was not found in the DB."))
    else:
        click.echo(success(f"The value '{val}' was found at db['{key}']"))
        flag = str(input("Confirm delete? (y/n): "))
        click.echo()

        if flag == "y":
            del database[key]
            click.echo(success(f"db['{key}'] was successfully deleted."))
        else:
            click.echo(info(f"Delete operation cancelled."))


@cli.command(name="nuke")
def nuke_db():
    """Wipes ALL key-value pairs in the DB."""

    flag = str(input("Are you sure you want to nuke the DB? (y/n):"))

    if flag == "y":
        flag = str(input("Ok, but like, REALLY sure? (y/n):"))

        if flag == "y":
            click.echo(info("Beginning Nuke operation...\n"))

            keys = list(database.keys())
            for k in keys: del database[k]

            click.echo(success("Nuke operation successful."))
        else:
            click.echo(info("Nuke operation cancelled. (close one!)"))
    else:
        click.echo(info("Nuke operation cancelled."))        



@cli.command(name="all")
@click.argument("file_path", default="db_all.json")
def list_all(file_path: str):
    """Writes all keys and values in the DB to a JSON file."""

    try:
        file = open(file_path, 'w+')
    except:
        click.echo(failure(f"No such file or directory '{file_path}'"))
    else:
        keys = list(database.keys())
        binds = dict([(k, database[k]) for k in keys])
        
        json.dump(binds, file)

        click.echo(success(f"Output successfully dumped to '{file_path}'"))


if __name__ == "__main__":
    cli(prog_name="repldb")
