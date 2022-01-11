from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import get_user_object_from_token_or_abort
from pony.orm import db_session


class LegacyLikeFilterByPost(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Authentication token", required=True)
        parser.add_argument("post_id", type=int, help="Post ID to get likes for", required=True)
        parser.add_argument("count", type=int, help="Amount of likes to get", required=True)
        parser.add_argument("offset", type=int, help="Offset to get from", required=True)

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        post = db.Post.get(id=args['post_id'])
        if post is None:
            return {}, 404

        like_ids = []
        likes = post.likes
        for like in likes:
            like_ids.append(like.id)

        return like_ids, 201