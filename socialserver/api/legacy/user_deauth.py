#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.util.auth import (
    verify_password_valid,
    get_user_object_from_token_or_abort,
)
from socialserver.constants import LegacyErrorCodes
from pony.orm import db_session


# removes all sessions from a user
class LegacyAllDeauth(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        self.post_parser.add_argument(
            "password",
            type=str,
            required=True,
            help="Account password for confirmation",
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        if not verify_password_valid(
            args["password"], user.password_salt, user.password_hash
        ):
            return {"err": LegacyErrorCodes.INCORRECT_PASSWORD.value}, 401

        for session in user.sessions:
            session.delete()

        return {}, 201
