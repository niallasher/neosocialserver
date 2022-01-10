from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import verify_password_valid, get_user_object_from_token_or_abort
from socialserver.constants import LegacyErrorCodes
from pony.orm import db_session, select


# removes all sessions from a user
class LegacyAllDeauth(Resource):

    @db_session
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("password", type=str, required=True, help="Account password for confirmation")
        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        if not verify_password_valid(args['password'], user.password_salt, user.password_hash):
            return {"err": LegacyErrorCodes.INCORRECT_PASSWORD.value}, 401

        for session in user.sessions:
            session.delete()

        return {}, 201
