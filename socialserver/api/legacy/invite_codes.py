#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from pony.orm import db_session
from socialserver.util.auth import get_user_object_from_token_or_abort

"""
    this class is somewhat of a stub, since invite codes are not
    planned for support in 3.x as of now, therefore it always returns
    empty on a successful request, since the old client still calls it
    sometimes for whatever reason? who knows.
    
    we do retain the auth though, to keep some level of interface
    compatibility intact.
"""


class LegacyInviteCodes(Resource):
    @db_session
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "session_token", type=str, help="Session authentication key", required=True
        )
        args = parser.parse_args()

        get_user_object_from_token_or_abort(args["session_token"])

        # here's the stub part :)
        return [], 201
