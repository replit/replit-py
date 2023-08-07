"""Python implementation of ReplAuth"""

from json import dumps
from flask import Request
from typing import Optional

__all__ = ("getUserInfo")

class User:
  def __init__(self, request: Request):
    self.id = None
    self.name = None
    self.bio = None
    self.profile_image = None
    self.roles = None
    self.teams = None
    self.url = None
    if not request.headers.get('X-Replit-User-Id'): return

    REPLIT_HEADERS = list(filter(
      lambda header: header[0].startswith("X-Replit-User-"),
      list(request.headers)
    ))

    for header in REPLIT_HEADERS:
      header, value = header

      if header == "X-Replit-User-Id":
        value = int(value)
      elif header == "X-Replit-User-Teams" or header == "X-Replit-User-Roles":
        value = value.split(',')
      
      setattr(self, header[14:len(header)].lower().replace('-', '_'), value)

  def __repr__(self) -> str:
    return dumps(self.__dict__)

  def __str__(self) -> str:
    return self.name if self.name else ""

def getUserInfo(request: Request) -> Optional[User]:
  user = User(request)

  return user if user.id else None

    
      