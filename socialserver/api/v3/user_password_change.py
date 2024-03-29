#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.db import db
from pony.orm import db_session, select
from socialserver.constants import ErrorCodes, MIN_PASSWORD_LEN, MAX_PASSWORD_LEN
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import (
    verify_password_valid,
    auth_reqd,
    get_user_from_auth_header,
    hash_password,
    generate_salt,
    get_user_session_from_header,
)


class UserPasswordChange(Resource):
    def __init__(self):
        self.patch_parser = reqparse.RequestParser()
        self.patch_parser.add_argument("old_password", type=str, required=True)
        self.patch_parser.add_argument("new_password", type=str, required=True)
        # assumed to be false if not given.
        self.patch_parser.add_argument("delete_other_sessions", type=bool, required=False)

    @db_session
    @auth_reqd
    # patch not post, since we're not creating a new resource.
    def patch(self):
        # Should TOTP be required? I'm thinking no, because it's for keeping a session safe,
        # and you already need to be signed in to change the password. Worth considering though.
        args = self.patch_parser.parse_args()
        user = get_user_from_auth_header()

        delete_other_sessions = args.delete_other_sessions or False

        new_password = args.new_password

        if not verify_password_valid(
                args.old_password, user.password_salt, user.password_hash
        ):
            return format_error_return_v3(ErrorCodes.INCORRECT_PASSWORD, 401)

        if len(new_password) > MAX_PASSWORD_LEN or len(new_password) < MIN_PASSWORD_LEN:
            return format_error_return_v3(ErrorCodes.PASSWORD_NON_CONFORMING, 400)

        new_password_salt = generate_salt()
        new_password_hash = hash_password(new_password, new_password_salt)

        user.password_hash = new_password_hash
        user.password_salt = new_password_salt

        if delete_other_sessions:
            cur_session = get_user_session_from_header()
            sessions = select(s for s in user.sessions if s is not cur_session)
            for s in sessions:
                s.delete()

        return {}, 201
