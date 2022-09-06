from dataclasses import dataclass


# create a login exception with message
@dataclass
class LoginException(Exception):
    message: str