#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.constants import (
    MAX_FEED_GET_COUNT,
    ErrorCodes,
    PostAdditionalContentTypes,
)
from socialserver.db import db
from socialserver.util.api.v3.post import format_post_v3, format_userdata_v3
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from pony.orm import db_session
from pony import orm


class PostFeed(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("count", type=int, required=True)
        # maybe we should just assume zero if an offset isn't specified?
        # but I think it's better to be explicit about including it, as
        # otherwise I can see myself or others forgetting it, and wondering
        # why the same posts keep popping up.
        self.get_parser.add_argument("offset", type=int, required=True)
        # a list of usernames. if supplied, only posts from those
        # usernames will be shown
        self.get_parser.add_argument(
            "username", type=str, required=False, action="append"
        )
        # basically shorthand for specifying every username in the request.
        # takes precedence over any usernames appended (overwrites any given
        # usernames with the follower list)
        self.get_parser.add_argument("following_only", type=bool, required=False)

    @db_session
    @auth_reqd
    def get(self):
        args = self.get_parser.parse_args()

        if args["count"] > MAX_FEED_GET_COUNT:
            return {"error": ErrorCodes.FEED_GET_COUNT_TOO_HIGH.value}, 400

        requesting_user_db = get_user_from_auth_header()

        # we don't want to show users that are blocked
        # in the feed ofc.
        # NOTE: honestly, blocking is a bad name for this,
        # and should probably be changed.
        # (don't be surprised if this is still the same
        # 5 years from this comment)

        # seems like pycharm doesn't see the pony object as iterable
        # it is, so we're safe to do this.
        # noinspection PyTypeChecker
        blocks = orm.select(
            b.blocking for b in db.Block if b.user == requesting_user_db
        )[:]

        filtered = False
        filter_list = []

        if args["username"] is not None:
            filtered = True
            filter_list = args["username"]

        if args["following_only"]:
            filtered = True
            filter_list = orm.select(
                f.following.username for f in requesting_user_db.following
            )[::]

        if filtered:
            # noinspection PyTypeChecker
            query = (
                orm.select(
                    p
                    for p in db.Post
                    if p.user not in blocks
                    and p.under_moderation is False
                    and p.processed is True
                    and p.user.username in filter_list
                )
                .order_by(orm.desc(db.Post.creation_time))
                .limit(args.count, offset=args.offset)[::]
            )
        else:
            # noinspection PyTypeChecker
            query = (
                orm.select(
                    p
                    for p in db.Post
                    if p.user not in blocks
                    and p.under_moderation is False
                    and p.processed is True
                )
                .order_by(orm.desc(db.Post.creation_time))
                .limit(args.count, offset=args.offset)[::]
            )

        # TODO: this shares a schema with the single post
        # thing, so they should be common. maybe a class
        # that serializes to a dict? idk.
        posts = []
        for post in query:

            user_has_liked_post = (
                db.PostLike.get(user=requesting_user_db, post=post) is not None
            )

            user_owns_post = post.user == requesting_user_db

            additional_content_type = PostAdditionalContentTypes.NONE.value
            additional_content = []

            post_images = post.get_images
            video = post.video

            # images override anything else, since you can only have 1 additional content type. (for now)
            if len(post_images) >= 1:
                additional_content_type = PostAdditionalContentTypes.IMAGES.value
                for image in post_images:
                    additional_content.append(
                        {"identifier": image.identifier, "blurhash": image.blur_hash}
                    )
            elif video is not None:
                additional_content_type = PostAdditionalContentTypes.VIDEO.value
                additional_content.append(
                    {
                        "identifier": video.identifier,
                        "thumbnail_identifier": video.thumbnail.identifier,
                        "thumbnail_blurhash": video.thumbnail.blur_hash,
                    }
                )

            posts.append(
                {
                    "post": format_post_v3(post),
                    "user": format_userdata_v3(post.user),
                    "meta": {
                        "user_likes_post": user_has_liked_post,
                        "user_owns_post": user_owns_post,
                    },
                }
            )

        return {
            "meta": {
                # if we have less posts left than the user
                # asked for, we must have reached the end!
                "reached_end": len(posts)
                < args["count"]
            },
            "posts": posts,
        }, 201
