#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.constants import LegacyErrorCodes, AccountAttributes, LegacyAdminUserModTypes
from pony.orm import db_session


class LegacyAdminUserMod(Resource):

    @db_session
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("modtype", type=str, help="Modification Type")
        parser.add_argument("username", type=str, help="Username")

        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args['session_token'])

        if not r_user.is_admin:
            return {"err": LegacyErrorCodes.USER_NOT_ADMIN.value}, 401

        user = db.User.get(username=args['username'])
        # old server never checked this. shocker.
        if user is None:
            return {}, 404

        # toggle verification status
        if args['modtype'] == LegacyAdminUserModTypes.VERIFICATION_STATUS.value:
            if user.is_verified:
                user.account_attributes.remove(AccountAttributes.VERIFIED.value)
            else:
                user.account_attributes.append(AccountAttributes.VERIFIED.value)
            return {}, 201
        # toggle mod status

        elif args['modtype'] == LegacyAdminUserModTypes.MODERATOR_STATUS.value:
            if user.is_moderator:
                user.account_attributes.remove(AccountAttributes.MODERATOR.value)
            else:
                user.account_attributes.append(AccountAttributes.MODERATOR.value)
            return {}, 201

        # yep, you're seeing that right.
        # return error code 500
        # as in, internal server error 500.
        # even though
        # there wasn't an internal server error.
        # wild. and also actually used in the old client iirc.
        # so we *definitely* can't change it. great!
        return {}, 500
