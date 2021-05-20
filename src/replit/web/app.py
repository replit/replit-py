# flake8: noqa
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List
import flask

from ..database.database import ObservedDict, ObservedList

@dataclass
class ReplitUserContext:
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


class ReplitRequest(flask.Request):
    """Represents a client request."""

    auth: ReplitUserContext

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes request and runs update_auth.

        Args:
            args (Any): The arguments to be passed to the superclass.
            kwargs (Any): The keyword arguments to be passed to the superclass.
        """
        super().__init__(*args, **kwargs)
        self.update_auth()

    def update_auth(self) -> None:
        """Update the auth property to be a ReplitUserContext."""
        self.auth = ReplitUserContext.from_headers(self.headers)

    @property
    def is_authenticated(self) -> bool:
        """Check whether the user is authenticated with Replit.

        Returns:
            bool: Whether or not the user is signed in
        """
        return self.auth.is_authenticated

    @property
    def is_authed(self) -> bool:
        """Check whether the user is authenticated with Replit.

        Returns:
            bool: Whether or not the user is signed in
        """
        return self.auth.is_authenticated


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObservedDict) or isinstance(o, ObservedList):
            return o.value
        return super().default(o)


class ReplitApp(flask.Flask):
    """Represents a web application."""

    request_class = ReplitRequest
    json_encoder = JSONEncoder

    def __init__(
        self, import_name: str, nice_jinja: bool = True, **kwargs: Any
    ) -> None:
        """Initialize the app.

        Args:
            import_name (str): The name of the app, usually __name__
            nice_jinja (bool): Whether to change jinja settings to make them
                prettier. Defaults to True.
            **kwargs (Any): Extra keyword arguments to be passed to the flask init
                function.
        """
        super().__init__(import_name, **kwargs)
        if nice_jinja:
            self.jinja_env.trim_blocks = True
            self.jinja_env.lstrip_blocks = True

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Interface with the underlying Flask instance's run function.

        Args:
            args (Any): The arguments to be passed to the superclass' run method.
            kwargs (Any): The keyword arguments to be passed to the superclass' run
                method.

        Returns:
            Any: The result of running the superclasses' run method.
        """
        return super().run(*args, **kwargs)

    def run(self, port: int = 8080, localhost: bool = False, **kwargs: Any) -> None:
        """Run the app.

        Args:
            port (int): The port to run the app on. Defaults to 8080.
            localhost (bool): Whether to run the app without exposing it on all
                interfaces. Defaults to False.
            **kwargs (Any): Extra keyword arguments to be passed to the flask app's run
                method.
        """
        super().run(host="localhost" if localhost else "0.0.0.0", port=port, **kwargs)

    def debug(
        self,
        watch_dirs: List[str] = None,
        watch_files: List[str] = None,
        port: int = 8080,
        localhost: bool = False,
        **kwargs: Any
    ) -> None:
        """Run the app in debug mode.

        Args:
            watch_dirs (List[str]): Directories whose files will be added to
                watch_files. Defaults to [].
            watch_files (List[str]): Files to watch, and if changes are detected
                the server will be restarted. Defaults to [].
            port (int): The port to run the app on. Defaults to 8080.
            localhost (bool): Whether to run the app without exposing it on all
                interfaces. Defaults to False.
            **kwargs (Any): Extra keyword arguments to be passed to the flask app's run
                method.
        """
        watch_files = list(watch_files or [])

        for directory in watch_dirs or []:
            if not isinstance(directory, Path):
                directory = Path(directory)
            watch_files += [str(f) for f in directory.iterdir() if f.is_file()]

        super().run(
            host="localhost" if localhost else "0.0.0.0",
            port=port,
            debug=True,
            extra_files=watch_files,
        )
