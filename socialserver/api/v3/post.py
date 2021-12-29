from datetime import datetime
import re
from flask_restful import Resource, reqparse
from socialserver.db import db
from pony.orm import db_session, commit
from socialserver.constants import MAX_IMAGES_PER_POST, POST_MAX_LEN, REGEX_HASHTAG, ErrorCodes
from socialserver.util.auth import get_user_from_auth_header, auth_reqd


class Post(Resource):

    @db_session
    @auth_reqd
    def post(self):

        parser = reqparse.RequestParser()
        # TODO: should probably make it possible for people to post
        # just images; socialserver 2.x didn't allow that, and people
        # complained quite a bit!
        parser.add_argument('text_content', type=str, required=True)
        # images optional.
        parser.add_argument('images', type=str,
                            required=False, action="append")
        args = parser.parse_args()

        user = get_user_from_auth_header()

        # make sure the post is conforming to length requirements.
        # we don't limit the characters used as of now. might look
        # into this later? probably not needed, but unicode can be weird.

        text_content = args['text_content']
        if len(text_content) >= POST_MAX_LEN:
            return {"error": ErrorCodes.POST_TOO_LONG.value}, 400

        # we want to store db refs to the images,
        # instead of retrieving them from id whenever
        # somebody wants the post, so we populate the images
        # array with them.
        images = []
        if args['images'] is not None:
            referenced_images = args['images']
            print(referenced_images)
            # we don't want people making giant
            # image galleries in a post. !! SHOULD ALSO
            # BE ENFORCED CLIENT SIDE FOR UX !!
            if len(referenced_images) > MAX_IMAGES_PER_POST:
                return {"error": ErrorCodes.POST_TOO_MANY_IMAGES.value}, 400
            # we replace each image with a reference to it in the database,
            # for storage
            for image_identifier in referenced_images:
                image = db.Image.get(identifier=image_identifier)
                if image is None:
                    return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404
                images.append(image)

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
                tag = db.Hashtag(creation_time=datetime.now(),
                                 name=tag_name)
            else:
                tag = existing_tag
            db_tags.append(tag)

        new_post = db.Post(
            under_moderation=False,
            user=user,
            creation_time=datetime.now(),
            text=text_content,
            images=images,
            hashtags=db_tags)

        # we commit earlier than normal, so we
        # can return the ID before the function ends
        # (the default decorator will only commit
        # the new post right at the end)
        commit()

        return {"post_id": new_post.id}, 200

    @db_session
    @auth_reqd
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('post_id', type=int, required=True)
        args = parser.parse_args()

        user = get_user_from_auth_header()

        wanted_post = db.Post.get(id=args['post_id'])
        if wanted_post is None:
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        # we don't want to show under moderation posts to normal users,
        # even if they explicitly request them (getting posts in a feed
        # will filter these out automatically)

        # we return POST_NOT_FOUND, so we don't explicitly highlight the
        # fact this post is moderated, just in case.
        if wanted_post.under_moderation is True and not (user.is_admin or user.is_moderator):
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        # if you've blocked a user, we don't want you to see their posts.
        if wanted_post.user in user.blocked_users:
            return {"error": ErrorCodes.USER_BLOCKED.value}, 400

        post_images = []
        for image in wanted_post.images:
            post_images.append(image.identifier)

        user_has_liked_post = db.PostLike.get(user=user,
                                              post=wanted_post) is not None

        user_owns_post = wanted_post.user == user

        return {
                   "post": {
                       "id": wanted_post.id,
                       "content": wanted_post.text,
                       "creation_date": wanted_post.creation_time.timestamp(),
                       "like_count": len(wanted_post.likes),
                       "comment_count": len(wanted_post.comments),
                       "images": post_images
                   },
                   "user": {
                       "display_name": wanted_post.user.display_name,
                       "username": wanted_post.user.username,
                       "verified": wanted_post.user.is_verified,
                       "profile_picture": (wanted_post.user.profile_pic.identifier
                                           if wanted_post.user.has_profile_picture else None),
                       "liked_post": user_has_liked_post,
                       "own_post": user_owns_post
                   },
               }, 201