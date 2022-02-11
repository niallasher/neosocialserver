from pony.orm import db_session, select
from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from datetime import datetime


class LegacyLike(Resource):

    @db_session
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Authentication token", required=True)
        parser.add_argument("post_id", type=int, help="PostID to toggle like on")

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        post = db.Post.get(id=args['post_id'])
        # the original didn't actually check this lol
        if post is None:
            return {}, 404

        existing_like = db.PostLike.get(user=user, post=post)

        if existing_like is None:
            db.PostLike(
                user=user,
                post=post,
                creation_time=datetime.utcnow()
            )
        else:
            existing_like.delete()

        like_count = select(like for like in db.PostLike
                            if like.post == post).count()

        return {
                   "postIsLiked": existing_like is None,
                   "postLikeCount": like_count
               }, 201

    @db_session
    def get(self):

        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Authentication Tokens", required=True)
        # this should be an int, but it wasn't in the old server, so it's a string.
        parser.add_argument("like_id", type=str, help="Authentication Tokens", required=True)

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        like = db.PostLike.get(id=args['like_id'])

        if like is None:
            return {}, 404

        user = like.user

        return {
                   "username": user.username,
                   "displayName": user.display_name
               }, 201
