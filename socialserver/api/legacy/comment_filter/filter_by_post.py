#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from pony.orm import db_session, select, desc
from socialserver.util.auth import get_user_object_from_token_or_abort
from flask_restful import Resource, reqparse


class LegacyCommentFilterByPost(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication token"
        )
        self.get_parser.add_argument(
            "post_id", type=int, required=True, help="Post ID to filter by"
        )
        self.get_parser.add_argument(
            "count", type=int, required=True, help="Amount of IDs to return"
        )
        self.get_parser.add_argument(
            "offset", type=int, required=True, help="Offset to filter by"
        )

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        post = db.Post.get(id=args["post_id"])
        if post is None:
            return {}, 404

        comment_query = (
            select(comment for comment in db.Comment if comment.post == post)
            .order_by(desc(db.Comment.id))
            .limit(args["count"], offset=args["offset"])
        )
        comment_ids = []
        for comment in comment_query:
            comment_ids.append(comment.id)

        return comment_ids, 201
