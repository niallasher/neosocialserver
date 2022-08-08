#  Copyright (c) Niall Asher 2022
import re
from datetime import datetime
from getpass import getpass

from socialserver.db import db
from socialserver.constants import REGEX_USERNAME_VALID, AccountAttributes
from pony import orm

from socialserver.util.auth import hash_password, generate_salt


class LoopInputBase():
    def __init__(self, prompt_string, regex=None, obscure=False, can_be_empty=False, valid_options=None):
        self.prompt_string = prompt_string
        self.regex = regex
        self.obscure = obscure
        self.can_be_empty = can_be_empty
        # if set to a list of options, input will be rejected if it doesn't match.
        self.valid_options = valid_options

    def get_input(self):
        while True:
            try:
                input_ok = True
                value = ""
                if self.obscure:
                    value = getpass(self.prompt_string)
                else:
                    value = input(self.prompt_string)
                if self.valid_options is not None and value.lower() not in self.valid_options:
                    input_ok = False
                if self.regex is not None and not bool(re.match(self.regex, value)):
                    input_ok = False
                if not self.can_be_empty and len(value) == 0:
                    input_ok = False
                if input_ok:
                    break
                print("Input was invalid. Please try again.")
                if not self.can_be_empty and len(value) == 0:
                    print("- Input cannot be empty.")
                if self.regex:
                    print(f"- Input must conform to regex: {self.regex}")
                if self.valid_options:
                    print(f"- Valid options: {self.valid_options}")
            except EOFError:
                print("Exiting on user request.")
                exit(0)
        return value


def _prompt_username_loop():
    while True:
        value = LoopInputBase("Username: ", regex=REGEX_USERNAME_VALID).get_input()
        existing_user = db.User.get(username=value)
        if existing_user is None:
            break
        print("Username already exists. Please choose another.")
    return value


@orm.db_session
def create_user_account():
    print("socialserver account creation wizard")
    print("this wizard has no magical powers. it's also scuffed.")
    print("please feel free to improve it.")
    print("")
    print(f"Choose a display name. It must conform to the following regex: [^.*]{1,32}$")
    display_name = LoopInputBase("Display name: ", regex="[^.*]{1,32}$", ).get_input()
    print(f"Choose a username. It must conform to the following regex: {REGEX_USERNAME_VALID}")
    username = _prompt_username_loop()
    print("Choose a password. It must be at least 8 characters long.")
    print("[!] Note: passwords will not be echoed.")
    while True:
        password = LoopInputBase("Password: ", regex=r"[^.*]{8,}", obscure=True).get_input()
        password_confirmation = LoopInputBase("Confirm Password: ", regex=r"[^.*]{8,}", obscure=True).get_input()
        if password_confirmation == password:
            break
        print("Sorry, those passwords didn't match. Please try again.")
    user_should_be_admin = LoopInputBase("User should be admin? [y/n/yes/no]: ",
                                         valid_options=["y","n","yes","no"]).get_input().lower() in ['y', 'yes']
    print("To review:")
    print(f"A{user_should_be_admin and 'n administrative' or ' normal'} user, named {username}, will be created.")
    is_correct = LoopInputBase("Is this correct? [y/n/yes/no]: ",
                               valid_options=["y", "n", "yes", "no"]).get_input().lower() in ['y', 'yes']
    if not is_correct:
        print("OK. Exiting without making changes to database.")
        exit(0)

    print("Hashing password...")
    salt = generate_salt()
    hash = hash_password(password, salt)

    db.User(
        display_name=display_name,
        username=username,
        password_hash = hash,
        password_salt = salt,
        creation_time = datetime.utcnow(),
        is_legacy_account=False,
        account_attributes = [AccountAttributes.ADMIN.value] if user_should_be_admin else [],
        bio="",
        recent_failed_login_count=0,
        account_approved=True
    )

    print("User created.")
