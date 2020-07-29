"""Utitilities for interacting with static files."""
import flask


class FileCache:
    """A simple cache for files."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.data = {}

    def add_to_cache(self, filename: str, content: str) -> None:
        """Add a filename to the cache.

        Args:
            filename (str): The filename to add.
            content (str): The content to add to the cache.
        """
        self.data[filename] = content

    def has(self, filename: str) -> bool:
        """Whether the cache has a certain filename.

        Args:
            filename (str): The filename to check for.

        Returns:
            bool: Whether the cache has filename.
        """
        return filename in self.data

    def invalidate(self, filename: str) -> None:
        """Remove a filename from the cache.

        Args:
            filename (str): The filename to remove.
        """
        try:
            self.data.pop(filename)
        except KeyError:
            pass

    def flush(self) -> None:
        """Remove all values from the cache."""
        self.data = {}


cache = FileCache()


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
                cache.add_to_cache(filename, self.content)

        super().__init__(self.content)
