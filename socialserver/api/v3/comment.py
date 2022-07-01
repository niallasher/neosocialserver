#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.constants import ErrorCodes, COMMENT_MAX_LEN
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from pony.orm import db_session, commit
from socialserver.db import db
from datetime import datetime


class Comment(Resource):
    def __init__(self):

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("text_content", type=str, required=True)
        self.post_parser.add_argument("post_id", type=int, required=True)

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument("comment_id", type=int, required=True)

    @db_session
    @auth_reqd
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_from_auth_header()

        post = db.Post.get(id=args.post_id)
        if post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        text = args.text_content

        # process comment
        text = text.replace("\n", "").strip()

        if len(text) > COMMENT_MAX_LEN:
            return format_error_return_v3(ErrorCodes.COMMENT_TOO_LONG, 400)

        if len(text) < 1:
            return format_error_return_v3(ErrorCodes.COMMENT_TOO_SHORT, 400)

        comment = db.Comment(
            user=user, creation_time=datetime.now(), text=text, post=post
        )

        # we commit to db here so that we can get the id from the comment,
        # to return it.
        commit()

        return {"id": comment.id}, 201

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_from_auth_header()

        comment = db.Comment.get(id=args.comment_id)
        if comment is None:
            return format_error_return_v3(ErrorCodes.COMMENT_NOT_FOUND, 404)

        if not comment.user == user:
            return format_error_return_v3(ErrorCodes.OBJECT_NOT_OWNED_BY_USER, 401)

        comment.delete()

        return {}, 200
