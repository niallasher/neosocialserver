#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from datetime import datetime
from flask_restful import Resource, reqparse
from pony.orm import db_session


class LegacyBlock(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        self.post_parser.add_argument(
            "username", type=str, required=True, help="Username to toggle block for"
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        user_to_block = db.User.get(username=args["username"])
        if user_to_block is None:
            return {}, 404

        # would be pretty funny if somebody screwed themselves like this lol
        if user == user_to_block:
            return {}, 401

        existing_block = db.Block.get(user=user, blocking=user_to_block)
        if existing_block is not None:
            existing_block.delete()
            return {"userBlocked": False}, 201

        db.Block(user=user, blocking=user_to_block, creation_time=datetime.utcnow())

        return {"userBlocked": True}, 201


# this is folded in here, since it's incredibly similar in scope.
# it allows to get a list of blocked users.
class LegacyUserBlocks(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        blocks = []
        for b in user.blocked_users:
            blocks.append(
                {
                    "username": b.blocking.username,
                    "displayName": b.blocking.display_name,
                }
            )

        return blocks, 201
