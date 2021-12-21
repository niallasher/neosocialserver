from datetime import datetime
from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import get_username_from_token
from socialserver.constants import ErrorCodes
from pony.orm import db_session


class Block(Resource):

    @db_session
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument("access_token", type=str, required=True)
        # the username to block
        parser.add_argument("username", type=str, required=True)
        args = parser.parse_args()

        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        requesting_user_db = db.User.get(username=requesting_user)

        user_to_follow = db.User.get(username=args['username'])
        if user_to_follow is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404
        if user_to_follow is requesting_user_db:
            return {"error": ErrorCodes.CANNOT_BLOCK_SELF.value}, 400

        existing_follow = db.Block.get(
            user=requesting_user_db,
            blocking=user_to_follow
        )
        if existing_follow is not None:
            return {"error": ErrorCodes.BLOCK_ALREADY_EXISTS.value}, 400

        db.Block(
            user=requesting_user_db,
            blocking=user_to_follow,
            creation_time=datetime.now()
        )

        return {}, 201

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument("access_token", type=str, required=True)
        parser.add_argument("username", type=str, required=True)
        args = parser.parse_args()

        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        requesting_user_db = db.User.get(username=requesting_user)

        user_to_unfollow = db.User.get(username=args['username'])
        if user_to_unfollow is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        existing_follow = db.Block.get(
            user=requesting_user_db,
            blocking=user_to_unfollow
        )

        if existing_follow is None:
            return {"error": ErrorCodes.CANNOT_FIND_BLOCK_ENTRY.value}, 404

        existing_follow.delete()
        return {}, 204
