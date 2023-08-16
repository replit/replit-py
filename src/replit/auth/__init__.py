"""Python implementation of ReplAuth"""

from json import dumps
from flask import Request
from typing import Optional

__all__ = ("get_user_info")

class User:
    id = name = bio = profile_image = roles = teams = url = None

    def __init__(self, request: Request):
        if not request.headers.get('X-Replit-User-Id'): return

        REPLIT_HEADERS = filter(
            lambda header: header[0].startswith("X-Replit-User-"),
            request.headers)

        for header in REPLIT_HEADERS:
            header, value = header

            if header == "X-Replit-User-Id":
                value = int(value)
            elif header in {"X-Replit-User-Teams", "X-Replit-User-Roles"}:
                value = value.split(',')

            setattr(self, header[14:len(header)].lower().replace('-', '_'),
                    value)

    def __repr__(self) -> str:
        return dumps(self.__dict__)

    def __str__(self) -> str:
        return self.name or ""


def get_user_info(request: Request) -> Optional[User]:
    user = User(request)

    return user if user.id else None
