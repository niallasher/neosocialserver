from socialserver.db import DbUser
import datetime
from pony.orm import db_session, commit
from socialserver.util.auth import generate_salt, hash_password
from constants import AccountAttributes


@db_session
def create():
    name = input('username: ')
    display_name = input('displayname: ')
    pw = input('password: ')
    bio = input('bio: ')
    salt = generate_salt()
    usr = DbUser(
        username=name,
        display_name=display_name,
        password_hash=hash_password(pw, salt),
        password_salt=salt,
        creation_time=datetime.datetime.now(),
        bio=bio,
        account_attributes=[AccountAttributes.VERIFIED.value, AccountAttributes.INSTANCE_ADMIN.value,
                            AccountAttributes.ADMIN.value, AccountAttributes.OG.value]
    )
    commit()
    print("ok, {}, {}".format(usr.id, usr.username))


create()
