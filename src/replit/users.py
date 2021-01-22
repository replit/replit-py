# TODO: provide a way to list repls.

import os

from requests import Session as HTTPSession
from requests_html import HTMLSession

# Environment variable configuration.
REPLIT_DOMAIN = os.environ.get("REPLIT_DOMAIN", "repl.it")

# Connection-pooling for HTTP requests.
http = HTTPSession()
html_http = HTMLSession()


class ReplitUser:
    """A Replit user's petadata."""
    def __init__(self, username=None):
        #: The profile's username.
        self.username = username
        #: The profile's given name.
        self.name = None
        #: The profile's given bio.
        self.bio = None
        #: The URL to the profile's avatar image.
        self.avatar_url = None

    def __repr__(self):
        return f'<ReplitUser "@{self.username}">'

    @property
    def as_dict(self):
        """The metadata of the given profile, as a dictionary."""
        return {
            "username": self.username,
            "name": self.name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
        }

    @staticmethod
    def _replit_url_from_username(username):
        """Construct a Replit URL from a username."""
        return f"https://{REPLIT_DOMAIN}/@{username}"

    @classmethod
    def from_username(_class, username):
        """Creates a new ReplitUser object from a given Repl.it profile name."""

        # TODO: catch non-existient users.
        url = _class._replit_url_from_username(username)

        # Fetch the profile from the web, and encapsulate its HTML.
        r = html_http.get(url=url)
        html = r.html

        # Instantiate the class.
        user = _class(username=username)

        # Populate the user instance from parsed HTML.
        user.name = user.__extract_name(html)
        user.bio = user.__extract_bio(html)
        user.avatar_url = user.__extract_avatar_url(html)

        return user

    @property
    def avatar_content(self):
        """The binary content of the user profile's avatar."""
        if self.avatar_url:
            return http.get(self.avatar_url).content

    def __extract_name(self, html):
        return html.find("h1", first=True).text

    def __extract_bio(self, html):
        return html.find(".Linkify", first=True).text

    def __extract_avatar_url(self, html):
        e = html.find(".profile-icon > span", first=True)
        style_str = e.attrs["style"]

        # Remove the CSS-y parts of the image URL, in a clear manner.
        len_0 = len('background-image:url("')
        len_1 = len('"]')

        # Slice the background string up.
        avatar_url = style_str[len_0 : (len(style_str) - len_1)]

        return avatar_url


def get_profile(username):
    """Creates a new ReplitUser object from a given Repl.it profile name."""

    return ReplitUser.from_username(username)


# Syntax suagar.
User = ReplitUser
