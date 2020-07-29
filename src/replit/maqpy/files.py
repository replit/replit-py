"""Utitilities for interacting with static files."""
import flask


cache = {}


class File(flask.Response):
    """Represents a static file."""

    def __init__(self, filename: str, no_cache: bool = False) -> None:
        """Initialize the file.

        Args:
            filename (str): The filename to read from.
            no_cache (bool): Whether to skip caching the file. Defaults to
                False.
        """
        self.filename = str(filename)
        self.no_cache = no_cache

        if filename in cache:
            self.content = cache[filename]
        else:
            with open(filename, "r") as f:
                self.content = f.read()

            if not no_cache:
                cache[filename] = self.content

        super().__init__(self.content)
