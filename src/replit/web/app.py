# flake8: noqa
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List
import flask

from ..database.database import ObservedDict, ObservedList

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


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, ObservedDict) or isinstance(o, ObservedList):
            return o.value
        return super().default(o)


def run_app(app: flask.Flask, host: str = "0.0.0.0", port: int = 8080, **kwargs) -> None:
    """A simple wrapper around app.run() with replit compatible defaults."""
    app.run(host=host, port=port, **kwargs)
