#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from pony.orm import db_session, select
from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from datetime import datetime


class LegacyFollower(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Tokens"
        )
        self.post_parser.add_argument(
            "username", type=str, required=True, help="Username to follow"
        )

        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Tokens"
        )
        self.get_parser.add_argument(
            "username", type=str, required=True, help="Username to follow"
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])
        user_to_follow = db.User.get(username=args["username"])
        if user_to_follow is None:
            return {}, 404

        # we don't want people following themselves
        # because that's just sad :(
        if user == user_to_follow:
            return {}, 401

        existing_follow = db.Follow.get(user=user, following=user_to_follow)

        current_follow_count = select(
            f for f in db.Follow if f.following == user_to_follow
        ).count()

        if existing_follow is not None:
            existing_follow.delete()
            return {
                "userIsFollowed": False,
                "userFollowCount": current_follow_count - 1,
            }, 201

        db.Follow(user=user, following=user_to_follow, creation_time=datetime.utcnow())

        return {
            "userIsFollowed": True,
            "userFollowCount": current_follow_count + 1,
        }, 201

    @db_session
    # this is a weird one as you can see. IIRC it's used by the follower lists, just to
    # get the display name.
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        follower = db.User.get(username=args.username)

        if follower is None:
            return {}, 404

        return {
            "username": follower.username,
            "displayName": follower.display_name,
        }, 201
