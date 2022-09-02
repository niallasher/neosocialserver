#  Copyright (c) Niall Asher 2022
from flask_restful import Resource, reqparse

from socialserver.constants import ErrorCodes, MAX_FEED_GET_COUNT
from socialserver.db import db
from socialserver.util.api.v3.data_format import format_post_v3, format_userdata_v3
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from pony.orm import db_session
from pony import orm


class BookmarkPost(Resource):

    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("post_id", type=int, required=True)

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument("post_id", type=int, required=True)

    @db_session
    @auth_reqd
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_from_auth_header()

        post = db.Post.get(id=args.post_id)
        if post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        # check if the post is already bookmarked, and fail out if it is.
        if post in user.bookmarks:
            return format_error_return_v3(ErrorCodes.POST_ALREADY_BOOKMARKED, 400)

        user.bookmarks.add(post)

        return {"post_bookmarked": True}, 200

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_from_auth_header()

        post = db.Post.get(id=args.post_id)
        if post not in user.bookmarks:
            return format_error_return_v3(ErrorCodes.POST_NOT_BOOKMARKED, 400)

        # bookmarks is an unordered set, and for whatever reason, the .discard built-in
        # doesn't work on PonyORMs implementation of set, so we convert it to a list.

        # TODO: investigate if there is another way to remove a specific item from a Pony set \
        # so we can avoid converting.
        bookmarks_list = list(user.bookmarks)
        bookmarks_list.remove(post)
        user.bookmarks = set(bookmarks_list)

        return {"post_bookmarked": False}, 200


class BookmarkFeed(Resource):

    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("count", type=int, required=True)
        self.get_parser.add_argument("offset", type=int, required=True)

    @db_session
    @auth_reqd
    def get(self):
        args = self.get_parser.parse_args()

        if args.count > MAX_FEED_GET_COUNT:
            return format_error_return_v3(ErrorCodes.FEED_GET_COUNT_TOO_HIGH, 400)

        requesting_user_db = get_user_from_auth_header()

        # TODO: should we show bookmarks from blocked users? not sure about this.
        # we will for now.

        query = orm.select(
            p for p in requesting_user_db.bookmarks if p.processed is True and p.under_moderation is False
        ).order_by(orm.desc(db.Post.id)).limit(args.count, offset=args.offset)[::]

        posts = []
        for post in query:
            user_has_liked_post = db.PostLike.get(user=requesting_user_db, post=post) is not None
            user_owns_post = post.user == requesting_user_db

            # TODO: we should really have pydantic models for returns to ensure all stay up to date
            # and valid.
            posts.append(
                {
                    "post": format_post_v3(post),
                    "user": format_userdata_v3(post.user),
                    "meta": {
                        "user_likes_post": user_has_liked_post,
                        "user_owns_post": user_owns_post
                    }
                }
            )

        return {
                   "meta": {
                       "reached_end": len(posts) < args["count"]
                   },
                   "posts": posts
               }, 201
