#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.constants import MAX_FEED_GET_COUNT
from pony.orm import db_session, select, desc


class LegacyPostFilterByUser(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        # this slightly breaks compat, but it could cause crashes in the original server, so we're changing it
        # (nothing *should* have been omitting these)
        self.get_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        self.get_parser.add_argument(
            "count", type=int, help="Amount of posts to return", required=True
        )
        self.get_parser.add_argument(
            "offset", type=int, help="Amount of posts to skip.", required=True
        )
        self.get_parser.add_argument(
            "users", action="append", help="Users to filter by", required=True
        )

    @db_session
    def get(self):

        args = self.get_parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args["session_token"])

        if args["count"] > MAX_FEED_GET_COUNT:
            return {}, 400

        # add every valid user from the request into a list,
        # to filter by later.
        users = []

        for username in args["users"]:
            user = db.User.get(username=username)
            if user is not None:
                users.append(user)

        # error out if there were *no* valid usernames given
        if len(users) == 0:
            return {}, 406

        blocks = select(b.blocking for b in db.Block if b.user == r_user)[:]

        query = (
            select(
                p
                for p in db.Post
                if p.user not in blocks and p.user in users and not p.under_moderation
            )
            .order_by(desc(db.Post.id))
            .limit(args["count"], offset=args["offset"])
        )

        post_ids = []
        for post in query:
            post_ids.append(post.id)

        return post_ids, 201
