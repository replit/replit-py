"""Information about your repl."""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ReplInfo:
    id: Optional[str] = os.getenv("REPL_ID")
    slug: Optional[str] = os.getenv("REPL_SLUG")
    owner: Optional[str] = os.getenv("REPL_OWNER")
    language: Optional[str] = os.getenv("REPL_LANGUAGE")

    @property
    def id_co_url(self) -> Optional[str]:
        """The hosted URL of the repl in the form https://<id>.id.repl.co."""
        if self.id:
            return f"https://{self.id}.id.repl.co"
        return None

    @property
    def co_url(self) -> Optional[str]:
        """The readable, hosted repl.co URL for this repl."""
        if self.slug and self.owner:
            return f"https://{self.slug.lower()}.{self.owner.lower()}.repl.co"
        return None

    @property
    def replit_url(self) -> Optional[str]:
        """The URL of this repl on replit.com."""
        if self.slug and self.owner:
            return f"https://replit.com/@{self.owner}/{self.slug}"
        return None

    @property
    def replit_id_url(self) -> Optional[str]:
        """The URL of this repl on replit.com, based on the repl's ID."""
        if self.id:
            return f"https://replit.com/replid/{self.id}"
        return None

    @staticmethod
    def from_env_variables() -> 'ReplInfo':
        return ReplInfo()

    @staticmethod
    def from_values(
        id: Optional[str] = None,
        slug: Optional[str] = None,
        owner: Optional[str] = None,
        language: Optional[str] = None
    ) -> 'ReplInfo':
        return ReplInfo(id, slug, owner, language)

    def __repr__(self) -> str:
        return (f"ReplInfo(id={self.id}, slug={self.slug}, owner={self.owner}, "
                f"language={self.language})")

    def __str__(self) -> str:
        return self.slug or ""
