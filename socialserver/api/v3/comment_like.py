#  Copyright (c) Niall Asher 2022

from socialserver.constants import ErrorCodes
from socialserver.db import db
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from flask_restful import reqparse, Resource
from pony.orm import db_session, commit, select
from datetime import datetime


class CommentLike(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("comment_id", type=int, required=True)

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument("comment_id", type=int, required=True)

    @db_session
    @auth_reqd
    def post(self):
        args = self.get_parser.parse_args()

        user = get_user_from_auth_header()

        comment = db.Comment.get(id=args["comment_id"])
        if comment is None:
            return {"error": ErrorCodes.COMMENT_NOT_FOUND.value}, 404

        existing_like = db.CommentLike.get(comment=comment, user=user)
        if existing_like is not None:
            return {"error": ErrorCodes.OBJECT_ALREADY_LIKED.value}, 400

        db.CommentLike(user=user, comment=comment, creation_time=datetime.now())

        # commit here so the count is up-to-date!
        commit()

        like_count = select(
            like for like in db.CommentLike if like.comment is comment
        ).count()

        return {"liked": True, "like_count": like_count}, 201

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_from_auth_header()

        comment = db.Comment.get(id=args["comment_id"])
        if comment is None:
            return {"error": ErrorCodes.COMMENT_NOT_FOUND.value}, 404

        existing_like = db.CommentLike.get(comment=comment, user=user)
        if existing_like is None:
            return {"error": ErrorCodes.OBJECT_NOT_LIKED.value}, 400

        existing_like.delete()

        like_count = select(
            like for like in db.CommentLike if like.comment is comment
        ).count()

        commit()

        return {"liked": False, "like_count": like_count}, 200
