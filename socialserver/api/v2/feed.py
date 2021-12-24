from flask_restful import Resource, reqparse
from socialserver.constants import MAX_FEED_GET_COUNT, ErrorCodes
from socialserver.db import db
from socialserver.util.auth import get_username_from_token
from pony.orm import db_session
from pony import orm


class PostFeed(Resource):

    @db_session
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('count', type=int, required=True)
        # maybe we should just assume zero if an offset isn't specified?
        # but I think it's better to be explicit about including it, as
        # otherwise I can see myself or others forgetting it, and wondering
        # why the same posts keep popping up.
        parser.add_argument('offset', type=int, required=True)
        # a list of usernames. if supplied, only posts from those
        # usernames will be shown
        parser.add_argument('username', type=str,
                            required=False, action="append")
        # basically shorthand for specifying every username in the request.
        # takes precedence over any usernames appended (overwrites any given
        # usernames with the follower list)
        parser.add_argument('following_only', type=bool, required=False)
        args = parser.parse_args()

        if args['count'] >= MAX_FEED_GET_COUNT:
            return {"error": ErrorCodes.FEED_GET_COUNT_TOO_HIGH.value}, 400

        requesting_user = get_username_from_token(args['access_token'], db)
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 403
        requesting_user_db = db.User.get(username=requesting_user)

        # we don't want to show users that are blocked
        # in the feed ofc.
        # NOTE: honestly, blocking is a bad name for this,
        # and should probably be changed.
        # (don't be surprised if this is still the same
        # 5 years from this comment)

        # seems like pycharm doesn't see the pony object as iterable
        # it is, so we're safe to do this.
        # noinspection PyTypeChecker
        blocks = orm.select(b.blocking for b in db.Block
                            if b.user == requesting_user_db)[:]

        filtered = False

        filter_list = []

        if args['username'] is not None:
            filtered = True
            filter_list = args['username']

        if args['following_only']:
            filtered = True
            filter_list = orm.select(f.user.username
                                     for f in requesting_user_db.following)

        if filtered:

            # noinspection PyTypeChecker
            query = orm.select(p for p in db.Post
                               if p.user not in blocks and p.under_moderation is False and p.user.username
                               in filter_list)
        else:
            # noinspection PyTypeChecker
            query = orm.select(p for p in db.Post
                               if p.user not in blocks and p.under_moderation is False).order_by(
                orm.desc(db.Post.creation_time)).limit(
                args.count, offset=args.offset
            )

        # TODO: this shares a schema with the single post
        # thing, so they should be common. maybe a class
        # that serializes to a dict? idk.
        posts = []
        for post in query:

            user_has_liked_post = db.PostLike.get(user=requesting_user_db,
                                                  post=post) is not None

            user_owns_post = post.user == requesting_user_db

            post_images = []
            for image in post.images:
                post_images.append(image.identifier)

            posts.append(
                {
                    "post": {
                        "id": post.id,
                        "content": post.text,
                        "creation_date": post.creation_time.timestamp(),
                        "like_count": len(post.likes),
                        "comment_count": len(post.comments),
                        "images": post_images
                    },
                    "user": {
                        "display_name": post.user.display_name,
                        "username": post.user.username,
                        "verified": post.user.is_verified,
                        "profile_picture": post.user.profile_pic.identifier if post.user.has_profile_picture else None,
                        "liked_post": user_has_liked_post,
                        "own_post": user_owns_post
                    }
                }
            )

        return {
                   "meta": {
                       # if we have less posts left than the user
                       # asked for, we must have reached the end!
                       "reached_end": len(query) < args['count']
                   },
                   "posts": posts
               }, 201
