"""Core of maqpi."""
from dataclasses import dataclass
from typing import Any

import flask


@dataclass
class ReplitAuthContext:
    """A dataclass defining a Repl Auth state."""

    user_id: int
    name: str
    roles: str

    @classmethod
    def from_headers(cls, headers: dict):
        """Initialize an instance using the Replit magic headers.

        Args:
            headers (dict): A dictionary of headers received

        Returns:
            [type]: An initialized class instance
        """
        return cls(
            user_id=headers.get("X-Replit-User-Id"),
            name=headers.get("X-Replit-User-Name"),
            roles=headers.get("X-Replit-User-Roles"),
        )

    @property
    def signed_in(self) -> bool:
        """Return whether or not the authentication is activated."""
        return self.name != ""


class Request(flask.Request):
    """Represents a client request."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize request and run update_auth."""
        super().__init__(*args, **kwargs)
        self.update_auth()

    def update_auth(self) -> None:
        """Update the auth property to be a ReplitAuthContext."""
        self.auth = ReplitAuthContext.from_headers(self.headers)

    @property
    def signed_in(self) -> bool:
        """Return whether or not the authentication is activated."""
        return self.auth.signed_in


class App(flask.Flask):
    """Represents a web application."""

    request_class = Request

    def all_pages_sign_in(self) -> None:
        """Require sign-in on all pages."""
        raise NotImplementedError()

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Interface with the underlying flask instance's run function."""
        return super().run(*args, **kwargs)

    def run(self, port: int = 8080, localhost: bool = False) -> None:
        """Run the app.

        Args:
            port (int): The port to run the app on. Defaults to 8080.
            localhost (bool): Whether to run the app without exposing it on all
                interfaces. Defaults to False.
        """
        super().run(host="localhost" if localhost else "0.0.0.0", port=port)
