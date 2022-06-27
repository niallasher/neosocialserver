#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from socialserver.constants import UserNotFoundException


def get_user_from_db(username) -> db.User:
    user = db.User.get(username=username)
    if user is None:
        raise UserNotFoundException
    return user
