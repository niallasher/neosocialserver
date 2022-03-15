#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.util.auth import get_user_object_from_token_or_abort
from pony.orm import db_session, select
from socialserver.db import db
from socialserver.util.image import get_image_data_url_legacy
from socialserver.constants import ImageTypes, COMMENT_MAX_LEN
from datetime import datetime


class LegacyComment(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        # legacy api shared one parser between get and post reqs, hence the help message,
        # and the lack of required=True
        self.get_parser.add_argument(
            "comment_id", type=int, help="Comment ID to get (get req only)"
        )

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        # these two were originally part of a single parser with the args in the GET function as well
        self.post_parser.add_argument(
            "post_id", type=int, help="Post to comment on (post req only)"
        )
        self.post_parser.add_argument(
            "comment", type=str, help="Comment to post (post req only)"
        )

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        # yep, this help was wrong originally.
        # yep, the help is wrong now.
        self.delete_parser.add_argument(
            "comment_id", type=int, help="Comment ID to get (get req only)"
        )

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        if args["comment_id"] is (None or ""):
            return {}, 400

        comment = db.Comment.get(id=args["comment_id"])
        if comment is None:
            return {}, 400

        is_own_comment = comment.user == user

        avatar_data = ""
        if user.profile_pic is not None:
            avatar_data = get_image_data_url_legacy(
                user.profile_pic.identifier, ImageTypes.PROFILE_PICTURE
            )

        like_count = select(
            like for like in db.CommentLike if like.comment == comment
        ).count()

        user_has_liked_comment = (
            db.CommentLike.get(user=user, comment=comment) is not None
        )

        return {
            "username": comment.user.username,
            "displayName": comment.user.display_name,
            "comment": comment.text,
            "isOwnComment": is_own_comment,
            "avatarData": avatar_data,
            "userVerified": comment.user.is_verified,
            "likeCount": like_count,
            "commentLiked": user_has_liked_comment,
        }, 201

    @db_session
    def post(self):

        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        if args.post_id is None:
            return {}, 400

        if args["comment"] is None:
            return {}, 400

        post = db.Post.get(id=args["post_id"])
        if post is None:
            return {}, 404

        # strip out newlines
        comment_text = args["comment"].replace("\n", "")

        # we do this after, since newlines have length, and this would allow
        # people to bypass the <= 0 length check if we didn't strip them first
        if len(comment_text) <= 0:
            return {}, 400

        if COMMENT_MAX_LEN:
            # only truncate, no fail; legacy api did this
            comment = comment_text[0 : COMMENT_MAX_LEN - 1]

        db.Comment(
            user=user, post=post, text=comment_text, creation_time=datetime.utcnow()
        )

        return {}, 201

    @db_session
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        comment = db.Comment.get(id=args["comment_id"])
        if comment is None:
            return {}, 404

        # admins can delete any comment, so they bypass the auth check.
        # might make a more robust system for this, but for
        # now just using the legacy version works fine
        if not comment.user == user and not user.is_admin:
            return {}, 401

        comment.delete()
        return {}, 201


# might move this one to it's own file later??
class LegacyCommentLike(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        self.post_parser.add_argument(
            "comment_id",
            type=int,
            required=True,
            help="Comment ID to toggle like state on",
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        comment = db.Comment.get(id=args["comment_id"])
        # yet another thing not checked by the original server :))))))))))
        if comment is None:
            return {}, 404

        existing_like = db.CommentLike.get(user=user, comment=comment)

        current_like_count = select(
            like for like in db.CommentLike if like.comment == comment
        ).count(0)

        if existing_like is None:
            db.CommentLike(user=user, comment=comment, creation_time=datetime.utcnow())
            return {"commentLiked": True, "likeCount": current_like_count + 1}, 201

        existing_like.delete()
        return {"commentLiked": False, "likeCount": current_like_count - 1}, 201
