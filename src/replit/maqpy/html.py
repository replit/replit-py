"""Class-representations for HTML elements."""
from abc import ABC
from dataclasses import dataclass

import flask


class HTMLElement(ABC):
    """Base class for an HTML element."""

    pass


@dataclass
class Paragraph:
    """Represents a Paragraph (p) tag."""

    content: str

    def __str__(self) -> str:
        return f"<p>{self.content}</p>"


class Page(flask.Response):
    """Represents an HTML page."""

    def __init__(self, title: str = None, head: str = "", body: str = "") -> None:
        self.title = title
        self.head = head
        self.body = body

        title_html = f"<title>{self.title}</title>\n    " if self.title else ""
        super().__init__(
            f"""<!DOCTYPE html>
<html>
<head>
    {title_html}{self.head}
</head>
<body>
    {self.body}
</body>
</html>"""
        )
