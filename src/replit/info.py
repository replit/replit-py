import os
from typing import Optional


class ReplInfo:
    @property
    def id(self) -> Optional[str]:
        """The id of the repl (REPL_ID environment variable)."""
        return os.getenv("REPL_ID")

    @property
    def slug(self) -> str:
        """The slug (name) of the repl (REPL_SLUG environement variable)."""
        return os.getenv("REPL_SLUG")

    @property
    def owner(self) -> str:
        """The owner of the repl (REPL_OWNER environment variable)."""
        return os.getenv("REPL_OWNER")

    @property
    def language(self) -> Optional[str]:
        """The language of the repl (REPL_LANGUAGE environment variable)."""
        return os.getenv("REPL_LANGUAGE")

    @property
    def id_co_url(self) -> Optional[str]:
        """The hosted URL of the repl in the form https://<id>.id.repl.co.

        Less readable than the vanity URL but guaranteed to work (the vanity URL might
        be too long for a certificate to be issued for it, causing it to break)."""
        repl_id = self.id
        if repl_id is None:
            return None
        return f"https://{repl_id}.id.repl.co"

    @property
    def co_url(self) -> Optional[str]:
        """The readable, hosted repl.co URL for this repl.

        See id_url for the difference between the hosted URL types."""
        slug = self.slug
        owner = self.owner
        if slug is None or owner is None:
            return None
        return f"https://{slug.lower()}.{owner.lower()}.repl.co"

    @property
    def replit_url(self) -> Optional[str]:
        """The URL of this repl on replit.com."""
        slug = self.slug
        owner = self.owner
        if slug is None or owner is None:
            return None
        return f"https://replit.com/@{owner}/{slug}"

    @property
    def replit_id_url(self) -> Optional[str]:
        """The URL of this repl on replit.com, based on the repl's ID."""
        repl_id = self.id
        if repl_id is None:
            return None
        return f"https://replit.com/replid/{repl_id}"
