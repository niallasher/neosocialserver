#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from pony.orm import db_session, select, desc
from socialserver.db import db
from socialserver.constants import LegacyErrorCodes
from socialserver.util.auth import get_user_object_from_token_or_abort


class LegacyModQueue(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        # this used to be required=False for some reason, but no server code
        # ever did anything if it was invalid, so why even keep it that way I guess?
        self.post_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        # same here
        self.post_parser.add_argument(
            "post_id", type=int, help="Post to hide and add", required=True
        )

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        self.delete_parser.add_argument(
            "post_id", type=int, help="Post to hide and add", required=True
        )

        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        self.get_parser.add_argument(
            "count", type=int, required=True, help="Amount of posts to return."
        )
        self.get_parser.add_argument(
            "offset", type=int, required=True, help="Amount of posts to skip."
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])
        if True not in [user.is_moderator, user.is_admin]:
            return {
                "err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
            }, 401

        post = db.Post.get(id=args["post_id"])
        if post is None:
            return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

        post.under_moderation = True
        return {}, 201

    @db_session
    def delete(self):

        args = self.delete_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])
        if True not in [user.is_moderator, user.is_admin]:
            return {
                "err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
            }, 401

        post = db.Post.get(id=args["post_id"])
        if post is None:
            return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

        post.under_moderation = False
        return {}, 201

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])
        if True not in [user.is_moderator, user.is_admin]:
            return {
                "err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE.value
            }, 401

        posts = (
            select(post for post in db.Post if post.under_moderation is True)
            .order_by(desc(db.Post.id))
            .limit(args["count"], offset=args["offset"])
        )
        post_ids = []
        for post in posts:
            post_ids.append(post.id)

        return post_ids, 201
