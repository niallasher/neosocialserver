from datetime import datetime
from getpass import getpass
from socialserver.db import DbUser
from socialserver.cli.inputhelpers import get_input_string, get_input_bool
from pony.orm import select, commit, db_session
from socialserver.constants import AccountAttributes
from socialserver.util.auth import generate_salt, hash_password

"""
  username_exists
  returns true if a username is taken.
  good to use for ux purposes, so we don't end up failing
  to create a user. will probably get moved to socialserver.util.user
  or smth later
"""


def username_exists(username):
    # seems like pycharm doesn't see the pony object as iterable
    # it is, so we're safe to do this.
    # noinspection PyTypeChecker
    user = select(u for u in DbUser if u.username == username)
    return user is not None


@db_session
def mk_user_interactive():
    acc_attribs = []
    if not get_input_bool("Are you sure you want to create a new user? (y/n)"):
        return 1
    username = get_input_string("Username: ")
    if username_exists(username):
        print("User already exists, aborting")
        return 1
    display_name = get_input_string("Display name: ")
    # get account attribs
    get_input_bool("User is instance admin? (y/n)") and acc_attribs.append(
        AccountAttributes.INSTANCE_ADMIN.value)
    get_input_bool(
        "User is admin (y/n)? ") and acc_attribs.append(AccountAttributes.ADMIN.value)
    get_input_bool("User is moderator (y/n)? ") and acc_attribs.append(
        AccountAttributes.MODERATOR.value)
    get_input_bool("User is verified (y/n)? ") and acc_attribs.append(
        AccountAttributes.VERIFIED.value)
    # get password
    while True:
        pw = getpass("Password (no echo): ")
        if pw != '':
            if pw == getpass("Confirm password (no echo): "):
                break
            print("Sorry, those didn't match. Please try again.")
    salt = generate_salt()
    pwh = hash_password(pw, salt)

    new_user = DbUser(
        username=username,
        display_name=display_name,
        creation_time=datetime.now(),
        is_legacy_account=False,
        password_hash=pwh,
        password_salt=salt,
        account_attributes=acc_attribs
    )

    commit()
    print(f"Created a new user with an id of {new_user.id}")
