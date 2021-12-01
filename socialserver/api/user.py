from re import I
from socialserver.db import DbUser
from flask_restful import Resource, reqparse
from socialserver.constants import ErrorCodes
from socialserver.util.auth import get_username_from_token
from pony.orm import db_session


class UserInfo(Resource):

    @db_session
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args()

        # in the future, we might not require sign-in for read only access
        # to some parts, but for now we do.
        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        wanted_user = DbUser.get(username=args['username'])
        if wanted_user is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        pfp = None
        header = None

        if wanted_user.profile_pic is not None:
            pfp = wanted_user.profile_pic.identifier

        if wanted_user.header_pic is not None:
            header = wanted_user.header_pic.identifier

        return {
            "username": wanted_user.username,
            "display_name": wanted_user.display_name,
            "birthday": wanted_user.birthday,
            "account_attributes": wanted_user.account_attributes,
            "bio":  wanted_user.bio,
            "follower_count": wanted_user.followers.count(),
            "following_count": wanted_user.following.count(),
            "profile_picture": pfp,
            "header": header
        }, 200
