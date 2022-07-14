#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from flask_restful import Resource, reqparse
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.util.config import config
from socialserver.util.filesystem import fs_images
from socialserver.util.image import get_image_data_url_legacy
from socialserver.constants import (
    LegacyErrorCodes,
    ImageTypes,
    MAX_FEED_GET_COUNT,
    POST_MAX_LEN,
    REGEX_HASHTAG,
    ROOT_DIR,
)
import re
from pony.orm import db_session, select, desc
from datetime import datetime
from base64 import b64encode
from PIL import Image
from io import BytesIO

SERVE_FULL_POST_IMAGES = config.legacy_api_interface.deliver_full_post_images

# preload video_unsupported_image, so we don't have to read it from disk every time.
with open(
    f"{ROOT_DIR}/resources/legacy/video_unsupported_legacy_client.jpg", "rb"
) as image_file:
    video_unsupported_image = (
        "data:image/jpg;base64," + b64encode(image_file.read()).decode()
    )


class LegacyPost(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "session_token", type=str, help="Key for session authentication."
        )
        self.post_parser.add_argument(
            "post_text", type=str, help="Text for post to contain.", required=True
        )
        self.post_parser.add_argument(
            "post_image_hash",
            type=str,
            help="Hash for image if wanted.",
            required=False,
        )

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        self.delete_parser.add_argument(
            "post_id", type=int, help="Post to remove.", required=True
        )

        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument(
            "session_token",
            type=str,
            help="Key for session authentication.",
            required=True,
        )
        self.get_parser.add_argument("count", type=int, help="amount to retrieve.")
        self.get_parser.add_argument("offset", type=int, help="amount to offset.")
        self.get_parser.add_argument(
            "post_id", type=int, help="Post ID to get.", default=None
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        text_content = args["post_text"]
        if len(text_content) > POST_MAX_LEN:
            # api v1 didn't error out here. this behaviour is
            # inconsistent with api v3, but it is here for compatibility.
            # ill consider causing an error later, but I am trying to avoid
            # causing unnecessary failures the old client wouldn't understand
            # for ux reasons.
            text_content = text_content[
                0 : POST_MAX_LEN - 1
            ]  # starting from 0, so -1 from POST_MAX_LEN!

        # strip out any newlines that have been put in
        text_content = text_content.replace("\n", "")

        attachments = []

        # the legacy api can only upload one image btw
        if args["post_image_hash"]:
            image = db.Image.get(identifier=args["post_image_hash"])
            # make sure the image actually exists
            if image is None:
                return {}, 404
            attachments.append({
                "type": "image",
                "identifier": image.identifier
            })

        # while the old api doesn't understand hashtags or anything,
        # we still want to make them for people using the new one!
        hashregex = re.compile(REGEX_HASHTAG)
        # the regex is case-insensitive,
        # but we want to store them lowercase in db anyway!
        tags = hashregex.findall(text_content.lower())

        # db_tags will be populated with each tag associated with the post.
        db_tags = []
        for tag_name in tags:
            existing_tag = db.Hashtag.get(name=tag_name)
            if existing_tag is None:
                tag = db.Hashtag(creation_time=datetime.utcnow(), name=tag_name)
            else:
                tag = existing_tag
            db_tags.append(tag)

        db.Post(
            under_moderation=False,
            user=user,
            creation_time=datetime.utcnow(),
            text=text_content,
            hashtags=db_tags,
            processed=True,
            attachments=attachments
        )

        # api v1 didn't return the post id.
        return {}, 201

    @db_session
    def delete(self):
        args = self.delete_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        post = db.Post.get(id=args["post_id"])
        if post is None:
            # original server doesn't even check,
            # so the client probably doesn't handle 404 very well
            # we'll send back a 401, since that's explicitly handled
            return {}, 401

        if post.user == user:
            post.delete()
            return {}, 201

        return {}, 401

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        # if a post id is specified, we want to grab
        # a single post, instead of a feed!
        if args.post_id is not None:
            post = db.Post.get(id=args["post_id"])
            if post is None:
                # should be a 404, but the old server did it this way :(
                # (yes, it does return not authorized if it can't find anything lol)
                return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

            if post.processed is False:
                return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

            if post.under_moderation and True not in [user.is_moderator, user.is_admin]:
                return {
                    "err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_VIEW_POST.value
                }, 401

            image_serve_type = (
                ImageTypes.POST if SERVE_FULL_POST_IMAGES else ImageTypes.POST_PREVIEW
            )

            image_data = ""

            attachments = post.attachments
            image_attachments = list(filter(lambda x: x['type'] == 'image', attachments))

            for image in image_attachments:
                image = db.Image.get(image["identifier"])
                if image is not None and image.processed is False:
                    return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

            # if there are only videos, we'll serve the video not supported stuff
            if len(image_attachments) == 0 and len(attachments) >= 1:
                if config.legacy_api_interface.provide_legacy_video_thumbnails:
                    # we use the first video in the attachments list
                    req_video = db.Video.get(
                        identifier=list(filter(lambda x: x['type'] == 'video', attachments))[0]['identifier'])
                    if (
                        not config.legacy_api_interface.provide_incompatible_video_thumbnail_text_overlay
                    ):
                        image_data = get_image_data_url_legacy(
                            req_video.thumbnail.identifier, image_serve_type
                        )
                    else:
                        # this should probably be pre-generated in the future,
                        # but for now it seems pretty quick.
                        thumbnail_data = BytesIO(
                            fs_images.readbytes(
                                f"/{req_video.thumbnail.sha256sum}"
                                + f"/{ImageTypes.POST_PREVIEW.value}_"
                                + f"{config.legacy_api_interface.image_pixel_ratio}x.jpg"
                            )
                        )
                        thumbnail = Image.open(thumbnail_data)
                        # we want the overlay to be of consistent size.
                        # we can safely assume its aspect ratio is 1:1 because
                        # it's cropped as such when generated.
                        if thumbnail.width < 512 or thumbnail.width > 512:
                            thumbnail = thumbnail.resize((512, 512))
                        overlay = Image.open(
                            f"{ROOT_DIR}/resources/legacy/video_unsupported_overlay.png"
                        )
                        thumbnail.paste(overlay, (0, 0), overlay)
                        output_buffer = BytesIO()
                        thumbnail.save(output_buffer, format="JPEG")
                        output_buffer.seek(0)
                        image_data = (
                            "data:image/jpg;base64,"
                            + b64encode(output_buffer.read()).decode()
                        )
                else:
                    image_data = video_unsupported_image
            elif len(attachments) >= 1:
                req_image = db.Image.get(identifier=image_attachments[0]["identifier"])
                image_data = get_image_data_url_legacy(req_image.identifier,
                                                       image_serve_type)

            is_own_post = post.user == user

            post_like_count = select(
                like for like in db.PostLike if like.post == post
            ).count()
            post_comment_count = select(
                comment for comment in db.Comment if comment.post == post
            ).count()

            user_liked_post = db.PostLike.get(user=user, post=post) is not None

            # TODO: send the default when I've figured out the best way to do so.
            profile_pic_data = ""
            if post.user.profile_pic is not None:
                profile_pic_data = get_image_data_url_legacy(
                    post.user.profile_pic.identifier, ImageTypes.PROFILE_PICTURE
                )

            return {
                "displayName": post.user.display_name,
                "username": post.user.username,
                "avatarData": profile_pic_data,
                "isVerified": post.user.is_verified,
                "postText": post.text,
                "imageData": image_data,
                "postDate": post.creation_time.strftime("%d/%m/%y"),
                "isOwnPost": is_own_post,
                "postID": post.id,
                "likeCount": post_like_count,
                "postLiked": user_liked_post,
                "commentCount": post_comment_count,
                "isHidden": post.under_moderation is True,
            }, 201

        # feed mode
        else:

            if None in [args["count"], args["offset"]]:
                return {}, 400

            # this is also a slight breaking change, but don't think there's any other option here
            if args["count"] >= MAX_FEED_GET_COUNT:
                return {}, 400

            blocks = select(b.blocking for b in db.Block if b.user == user)[:]
            query = (
                select(
                    p
                    for p in db.Post
                    if p.user not in blocks
                    and p.under_moderation is False
                    and p.processed is True
                )
                .order_by(desc(db.Post.id))
                .limit(args["count"], offset=args["offset"])
            )

            post_ids = []
            for post in query:
                post_ids.append(post.id)

            return post_ids, 201
