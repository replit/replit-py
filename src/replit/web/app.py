# flake8: noqa
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List
import flask

from ..database.database import ObservedDict, ObservedList, DBJSONEncoder


@dataclass
class ReplitAuthContext:
    """A dataclass defining a Replit Auth state."""

    user_id: int
    name: str
    roles: str

    @classmethod
    def from_headers(cls, headers: dict) -> Any:
        """Initialize an instance using the Replit identification headers.

        Args:
            headers (dict): A dictionary of headers received

        Returns:
            Any: An initialized class instance
        """
        return cls(
            user_id=headers.get("X-Replit-User-Id"),
            name=headers.get("X-Replit-User-Name"),
            roles=headers.get("X-Replit-User-Roles"),
        )

    @property
    def is_authenticated(self) -> bool:
        """Check whether the user is authenticated in with Replit Auth.

        Returns:
            bool: whether or not the authentication is activated.
        """
        return bool(self.name)

    @property
    def is_authed(self) -> bool:
        """Check whether the user is authenticated in with Replit Auth.

        Returns:
            bool: whether or not the authentication is activated.
        """
        return bool(self.name)


def run(
    app: flask.Flask,
    host: str = "0.0.0.0",
    port: int = 8080,
    change_encoder: bool = True,
    **kwargs
) -> None:
    """A simple wrapper around app.run() with replit compatible defaults."""
    # don't clobber user
    if change_encoder and app.json_encoder is flask.json.JSONEncoder:
        app.json_encoder = DBJSONEncoder
    app.run(host=host, port=port, **kwargs)


def debug(
    app: flask.Flask,
    watch_dirs: List[str] = None,
    watch_files: List[str] = None,
    **kwargs: Any
) -> None:
    """Run the app in debug mode.
    Args:
        watch_dirs (List[str]): Directories whose files will be added to
            watch_files. Defaults to [].
        watch_files (List[str]): Files to watch, and if changes are detected
            the server will be restarted. Defaults to [].
        **kwargs (Any): Extra keyword arguments to be passed to the flask app's run
            method.
    """
    watch_files = list(watch_files or [])

    for directory in watch_dirs or []:
        if not isinstance(directory, Path):
            directory = Path(directory)
        watch_files += [str(f) for f in directory.iterdir() if f.is_file()]

    run(
        app,
        debug=True,
        extra_files=watch_files,
        **kwargs,
    )
