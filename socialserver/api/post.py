from datetime import datetime
import re
from flask_restful import Resource, reqparse
from werkzeug.wrappers import request
from socialserver.db import DbImage, DbPost, DbPostLike, DbUser
from pony.orm import db_session
from socialserver.constants import POST_MAX_LEN, ErrorCodes
from socialserver.util.auth import get_username_from_token


class Post(Resource):

    @db_session
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('post_id', type=int, required=True)
        args = parser.parse_args()

        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error", ErrorCodes.TOKEN_INVALID.value}, 401

        wanted_post = DbPost.get(id=args['post_id'])
        if wanted_post is None:
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        # we don't want to show under moderation posts to normal users,
        # even if they explicitly request them (getting posts in a feed
        # will filter these out automatically)

        # we return POST_NOT_FOUND so we don't explicitly highlight the
        # fact this post is moderated, just in case.
        if wanted_post.under_moderation == True and not (requesting_user.is_admin() or requesting_user.is_moderator()):
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        # if you've blocked a user, we don't want you to see their posts.
        if wanted_post.user in requesting_user.blocked_users:
            return {"error", ErrorCodes.USER_BLOCKED.value}, 400

        post_images = []
        for image in wanted_post.images():
            post_images.append(image.identifier)

        user_has_liked_post = DbPostLike.get(user=requesting_user,
                                             post=wanted_post)

        return {
            "post": {
                "id": wanted_post.id,
                "content": wanted_post.text,
                "creation_date": wanted_post.creation_time,
                "like_count": len(wanted_post.likes),
                "comment_count": len(wanted_post.comments),
                "images": post_images
            },
            "user": {
                "display_name": wanted_post.user.username,
                "username": wanted_post.user.display_name,
                "verified": wanted_post.user.is_verified(),
                "profile_picture": wanted_post.user.profile_pic.identifier if wanted_post.user.has_profile_picture() else None,
                "liked_post": user_has_liked_post
            },
        }
