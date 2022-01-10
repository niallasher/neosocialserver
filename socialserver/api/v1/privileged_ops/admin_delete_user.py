from flask_restful import Resource, reqparse
from pony.orm import db_session
from socialserver.db import db
from socialserver.constants import LegacyErrorCodes
from socialserver.util.auth import get_user_object_from_token_or_abort, verify_password_valid


class LegacyAdminDeleteUser(Resource):

    @db_session
    def delete(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("username", type=str, required=True, help="Username to Admin Delete")
        parser.add_argument("password", type=str, required=True, help="Password for session account")

        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args['session_token'])

        if not r_user.is_admin:
            return {"err": LegacyErrorCodes.USER_NOT_ADMIN}, 401

        # this is a *super*-destructive action. we definitely want a password check here!
        if not verify_password_valid(args['password'], r_user.password_salt, r_user.password_hash):
            return {"err": LegacyErrorCodes.INCORRECT_PASSWORD}, 401

        user = db.User.get(username=args['username'])
        if user is None:
            return {"err": LegacyErrorCodes.USERNAME_NOT_FOUND.value}, 401

        if user.is_admin:
            # "Et tu, Brute?" followed by complete inaction.
            return {"err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_MODIFY_USER_DESTRUCTIVE}

        # rip bozo
        user.delete()
        return {}, 201
