"""Core of maqpy."""
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Set

import flask

from .utils import sign_in


@dataclass
class ReplitAuthContext:
    """A dataclass defining a Repl Auth state."""

    user_id: int
    name: str
    roles: str

    @classmethod
    def from_headers(cls, headers: dict) -> Any:
        """Initialize an instance using the Replit magic headers.

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
    def signed_in(self) -> bool:
        """Check whether the user is signed in with repl auth.

        Returns:
            bool: whether or not the authentication is activated.
        """
        return bool(self.name)


class Request(flask.Request):
    """Represents a client request."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes request and runs update_auth.

        Args:
            args (Any): The arguments to be passed to the superclass.
            kwargs (Any): The keyword arguments to be passed to the superclass.
        """
        super().__init__(*args, **kwargs)
        self.update_auth()

    def update_auth(self) -> None:
        """Update the auth property to be a ReplitAuthContext."""
        self.auth = ReplitAuthContext.from_headers(self.headers)

    @property
    def signed_in(self) -> bool:
        """Check whether the user is signed in with repl auth.

        Returns:
            bool: Whether or not the user is signed in
        """
        return self.auth.signed_in


class App(flask.Flask):
    """Represents a web application."""

    request_class = Request

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

    def login_wall(self, exclude: Set[str] = ("/",), handler: Callable = None,) -> None:
        """Require users to be logged-in on all pages.

        Args:
            exclude (Tuple[str]): The routes that should not require sign in.
                Defaults to just /.
            handler (Callable): The handler to call when the user is not signed in. If
                not provided, defaults to maqpy.signin()
        """
        self._lw_exclude = set(exclude) or set()
        self._lw_handler = handler or (lambda: sign_in())

    def _request_handler(self, rule: str, view_func: Callable) -> Callable:
        """Return a handler for a given request.

        This enables the all_pages_sign_in feature.

        Args:
            rule (str): The url that the route will be matched to
            view_func (Callable): The original view function that will be called.

        Returns:
            Callable: A handler that runs the middleware and calls the original function
        """

        @wraps(view_func)
        def handler(*args: Any, **kwargs: Any) -> Any:
            if (
                hasattr(self, "_lw_exclude")
                and self._lw_exclude is not None
                and rule not in self._lw_exclude
                and not flask.request.signed_in
            ):
                return self._lw_handler(*args, **kwargs)
            return view_func(*args, **kwargs)

        return handler

    def add_url_rule(
        self,
        rule: str,
        endpoint: str = None,
        view_func: Callable = None,
        provide_automatic_options: bool = None,
        **options: Any
    ) -> None:
        """Replaces view function with custom handler."""
        return super().add_url_rule(
            rule,
            endpoint=endpoint,
            view_func=self._request_handler(rule, view_func)
            if view_func is not None
            else view_func,
            provide_automatic_options=provide_automatic_options,
            **options
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Interface with the underlying flask instance's run function.

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
