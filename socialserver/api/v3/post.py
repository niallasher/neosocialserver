#  Copyright (c) Niall Asher 2022

from datetime import datetime
import re
from flask_restful import Resource, reqparse
from socialserver.db import db
from pony.orm import db_session, commit
from socialserver.constants import (
    MAX_IMAGES_PER_POST,
    POST_MAX_LEN,
    REGEX_HASHTAG,
    ErrorCodes,
    PostAdditionalContentTypes,
)
from socialserver.util.api.v3.data_format import format_post_v3, format_userdata_v3
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import get_user_from_auth_header, auth_reqd


class Post(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("text_content", type=str, required=True)
        # images & videos optional
        self.post_parser.add_argument(
            "images", type=str, required=False, action="append"
        )
        self.post_parser.add_argument("video", type=str, required=False)

        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("post_id", type=int, required=True)

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument("post_id", type=int, required=True)

    @db_session
    @auth_reqd
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_from_auth_header()

        # make sure the post is conforming to length requirements.
        # we don't limit the characters used as of now (except for newlines). might look
        # into this later? probably not needed, but unicode can be weird.

        text_content = args.text_content
        if len(text_content) > POST_MAX_LEN:
            return format_error_return_v3(ErrorCodes.POST_TOO_LONG, 400)

        # strip out any newlines. the client shouldn't allow users to add
        # them for UX purposes!
        text_content = text_content.replace("\n", "")

        additional_content = PostAdditionalContentTypes.NONE.value
        # images is just used for relationship purposes, and might be removed soon?
        # this is due to it being a set (in db), and therefore not being indexable,
        # and not keeping it's order
        processed = True
        images = None
        video = None
        image_ids = []

        if args.images is not None:
            images = []
            referenced_images = args.images
            # we don't want people making giant
            # image galleries in a post. !! SHOULD ALSO
            # BE ENFORCED CLIENT SIDE FOR UX !!
            if len(referenced_images) > MAX_IMAGES_PER_POST:
                return format_error_return_v3(ErrorCodes.POST_TOO_MANY_IMAGES, 400)
            # we replace each image with a reference to it in the database,
            # for storage
            for image_identifier in referenced_images:
                image = db.Image.get(identifier=image_identifier)
                if image.processed is False:
                    processed = False
                if image is None:
                    return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)
                images.append(image)
                image_ids.append(image.id)
        elif args.video is not None:
            video = db.Video.get(identifier=args.video)
            if video is None:
                return format_error_return_v3(ErrorCodes.OBJECT_NOT_FOUND, 404)
            video = args.video

        # checking for hashtags in the post content
        # hashtags can be 1 to 12 chars long and only alphanumeric.
        hashregex = re.compile(REGEX_HASHTAG)
        # the regex is actually case-insensitive,
        # but we store them in the database lowercase
        # and converting them here means we don't have
        # to loop over the created list.
        tags = hashregex.findall(text_content.lower())

        db_tags = []
        for tag_name in tags:
            existing_tag = db.Hashtag.get(name=tag_name)
            if existing_tag is None:
                tag = db.Hashtag(creation_time=datetime.utcnow(), name=tag_name)
            else:
                tag = existing_tag
            db_tags.append(tag)

        new_post = db.Post(
            under_moderation=False,
            user=user,
            creation_time=datetime.utcnow(),
            text=text_content,
            hashtags=db_tags,
            processed=processed,
        )

        if images is not None:
            new_post.images = images
            new_post.image_ids = image_ids

        if video is not None:
            new_post.video = db.Video.get(identifier=video)

        # we commit earlier than normal, so we
        # can return the ID before the function ends
        # (the default decorator will only commit
        # the new post right at the end)
        commit()

        return {"post_id": new_post.id, "processed": processed}, 200

    @db_session
    @auth_reqd
    def get(self):

        args = self.get_parser.parse_args()

        user = get_user_from_auth_header()

        wanted_post = db.Post.get(id=args["post_id"])
        if wanted_post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        # we don't want to show under moderation posts to normal users,
        # even if they explicitly request them (getting posts in a feed
        # will filter these out automatically)

        # we return POST_NOT_FOUND, so we don't explicitly highlight the
        # fact this post is moderated, just in case.
        if wanted_post.under_moderation is True and not (
            user.is_admin or user.is_moderator
        ):
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        # if you've blocked a user, we don't want you to see their posts.
        if wanted_post.user in user.blocked_users:
            return format_error_return_v3(ErrorCodes.USER_BLOCKED, 400)

        # if the post hasn't been processed, we're not returning it to the user.
        if wanted_post.processed is False:
            return format_error_return_v3(ErrorCodes.POST_NOT_PROCESSED, 404)

        user_has_liked_post = db.PostLike.get(user=user, post=wanted_post) is not None

        user_owns_post = wanted_post.user == user

        return {
            "post": format_post_v3(wanted_post),
            "user": format_userdata_v3(wanted_post.user),
            "meta": {
                "user_likes_post": user_has_liked_post,
                "user_owns_post": user_owns_post,
            },
        }, 201

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_from_auth_header()

        post = db.Post.get(id=args.post_id)
        if post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        if not post.user == user:
            return format_error_return_v3(ErrorCodes.OBJECT_NOT_OWNED_BY_USER, 401)

        post.delete()

        return {}, 200
