from socialserver.db import db
from flask_restful import Resource, reqparse
from socialserver.util.auth import get_user_object_from_token
from socialserver.util.image import get_image_data_url_legacy, check_image_exists
from socialserver.constants import LegacyErrorCodes, ImageTypes, MAX_FEED_GET_COUNT
from pony.orm import db_session, select, desc


class LegacyPost(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("session_token", type=str, help="Key for session authentication.", required=True)
        parser.add_argument("count", type=int, help="amount to retrieve.")
        parser.add_argument("offset", type=int, help="amount to offset.")
        parser.add_argument("post_id", type=int, help="Post ID to get.", default=None)

        args = parser.parse_args()

        user = get_user_object_from_token(args['session_token'])
        if user is None:
            return {}, 401

        # if a post id is specified, we want to grab
        # a single post, instead of a feed!
        if args.post_id is not None:
            post = db.Post.get(id=args['post_id'])
            if post is None:
                # should be a 404, but the old server did it this way :(
                # (yes, it does return not authorized if it can't find anything lol)
                return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 401

            if post.under_moderation and True not in [user.is_moderator, user.is_admin]:
                return {"err": LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_VIEW_POST.value}, 401

            image_data = ""
            images = post.get_images
            if len(images) >= 1:
                # the legacy api can only handle one image per post, so we're gonna send the first one.
                # in the future, we might stitch them together in a collage form, but for now I just want
                # basic functionality.
                image_data = get_image_data_url_legacy(images[0].identifier, ImageTypes.POST_PREVIEW)

            is_own_post = post.user == user

            post_like_count = select(like for like in db.PostLike
                                     if like.post == post).count()
            post_comment_count = select(comment for comment in db.Comment
                                        if comment.post == post).count()

            user_liked_post = db.PostLike.get(user=user, post=post) is not None

            # TODO: send the default when I've figured out the best way to do so.
            profile_pic_data = ""
            if post.user.profile_pic is not None:
                profile_pic_data = get_image_data_url_legacy(post.user.profile_pic.identifier,
                                                             ImageTypes.PROFILE_PICTURE)

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
                       "isHidden": post.under_moderation is True
                   }, 201

        # feed mode
        else:

            if None in [args['count'], args['offset']]:
                return {}, 400

            # also a slight breaking change, but don't think there's any other option here
            if args['count'] >= MAX_FEED_GET_COUNT:
                return {}, 400

            blocks = select(b.blocking for b in db.Block
                            if b.user == user)[:]
            query = select(p for p in db.Post if p.user not in blocks and p.under_moderation is False).order_by(
                desc(db.Post.id)).limit(args['count'], offset=args['offset'])

            post_ids = []
            for post in query:
                post_ids.append(post.id)

            return post_ids, 201
