#  Copyright (c) Niall Asher 2022
from socialserver.constants import AccountAttributes
from socialserver.db import db
from rich import print
from pony.orm import db_session


def _get_user(name):
    user_db = db.User.get(username=name)
    if user_db is None:
        print(f"[red]User, {name}, doesn't exist in the database.")
        exit(1)
    return user_db


# TODO: all these could be one (or 2? 1 for revoke?) function(s), \
# that takes one of the enums as an argument, then uses that as the role name, \
# and the value to modify!

@db_session
def verify_user(name):
    user = _get_user(name)
    if AccountAttributes.VERIFIED.value in user.account_attributes:
        print(f"[yellow]User, {name}, is already verified.")
        exit(1)
    user.account_attributes.append(AccountAttributes.VERIFIED.value)
    print(f"[green]User, {name}, is now verified!")


@db_session
def unverify_user(name):
    user = _get_user(name)
    if AccountAttributes.VERIFIED.value not in user.account_attributes:
        print(f"[yellow]User, {name}, is already un-verified.")
        exit(1)
    user.account_attributes.remove(AccountAttributes.VERIFIED.value)
    print(f"[green]User, {name}, is no longer verified.")


@db_session
def mod_user(name):
    user = _get_user(name)
    if AccountAttributes.MODERATOR.value in user.account_attributes:
        print(f"[yellow]User, {name}, is already a moderator.")
        exit(1)
    user.account_attributes.append(AccountAttributes.MODERATOR.value)
    print(f"[green]User, {name}, is now a moderator.")


@db_session
def unmod_user(name):
    user = _get_user(name)
    if AccountAttributes.MODERATOR.value not in user.account_attributes:
        print(f"[yellow]User, {name}, isn't a moderator.")
        exit(1)
    user.account_attributes.remove(AccountAttributes.MODERATOR.value)
    print(f"[green]User, {name}, is no longer a moderator.")


@db_session
def make_user_admin(name):
    user = _get_user(name)
    if AccountAttributes.ADMIN.value in user.account_attributes:
        print(f"[yellow]User, {name}, is already an admin.")
        exit(1)
    user.account_attributes.append(AccountAttributes.ADMIN.value)
    print(f"[green]User, {name}, is now an admin.")


@db_session
def remove_user_admin_role(name):
    user = _get_user(name)
    if AccountAttributes.ADMIN.value not in user.account_attributes:
        print(f"[yellow]User, {name}, isn't an admin.")
        exit(1)
    user.account_attributes.remove(AccountAttributes.ADMIN.value)
    print(f"[green]User, {name}, is no longer an admin.")
