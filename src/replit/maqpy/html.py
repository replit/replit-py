"""Python object representations of HTML."""
from abc import ABC

import flask


class HTMLElement(ABC):
    """Base class for an HTML element."""

    def __init__(self, content: str, **attrs: str) -> None:
        """Initialize the class.

        Args:
            content (str): The content inside the HTML tag.
            attrs (str): The attributes of tag.
        """
        self.content = content
        self.attrs = attrs

    def stringify_attrs(self) -> str:
        """Generate a string version of the tags attributes.

        Returns:
            str: A string in the form of attr1="value1" attr2="value2"
        """
        return " ".join(f'{name}="{value}"' for name, value in self.attrs.items())

    def __str__(self) -> str:
        """Generates an HTML representation of the tag."""
        attr_text = self.stringify_attrs()
        return (
            f"<{self.tagname}{' ' + attr_text if attr_text else ''}>{self.content}"
            f"</{self.tagname}>"
        )


class Paragraph(HTMLElement):
    """Represents a Paragraph (p) tag."""

    tagname = "p"


class Link(HTMLElement):
    """Represents a Link (a) tag."""

    tagname = "a"

    def __init__(self, content: str, href: str, **attrs: str) -> None:
        """Initialize the class.

        Args:
            content (str): The content of the link tag.
            href (str): The href attribute, where the link points to.
            attrs (str): Any additional attributes of the tag.
        """
        super().__init__(content, **{"href": href, **attrs})


class Page(flask.Response):
    """Represents an HTML page."""

    def __init__(self, title: str = None, head: str = "", body: str = "") -> None:
        """Initialize the class.

        Args:
            title (str): The title of the page. If not provided no title tag will be
                added.
            head (str): The HTML to put in the head of the page. Defaults to nothing.
            body (str): The HTML to put in the body of the page. Defaults to nothing.
        """
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
