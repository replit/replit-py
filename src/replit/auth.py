from json import dumps
from flask import Request
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    bio: str
    profile_image: str
    forwarded_for: str
    roles: list
    teams: list
    url: str

    @classmethod
    def from_request(cls, request: Request) -> Optional['User']:
        user_id = request.headers.get('X-Replit-User-Id')
        if user_id and user_id.isdigit():
            replit_headers = {
                key[14:].lower().replace('-', '_'): value
                for key, value in request.headers.items()
                if key.startswith('X-Replit-User-')
            }
          
            replit_headers['id'] = int(user_id)
            replit_headers['roles'] = replit_headers.get('roles', '').split(',')
            replit_headers['teams'] = replit_headers.get('teams', '').split(',')
            replit_headers['forwarded_for'] = request.headers.get('X-Forwarded-For')
            return cls(**replit_headers)
        else:
            return None

    def to_dict(self) -> dict:
        return {
            key: value
            for key, value in self.__dict__.items()
            if value is not None
        }

    def __repr__(self) -> str:
        return dumps(self.to_dict())

    def __str__(self) -> str:
        return self.name if self.name else ""

def get_user_info(request: Request) -> Optional[User]:
    return User.from_request(request)
