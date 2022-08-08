#  Copyright (c) Niall Asher 2022

#  Copyright (c) Niall Asher 2022
from socialserver.db import db
from socialserver.util.api.v3.data_format import format_userdata_v3
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from socialserver.constants import ErrorCodes, MAX_FEED_GET_COUNT
from pony.orm import db_session, select, desc
from flask_restful import Resource, reqparse
from socialserver.util.api.v3.error_format import format_error_return_v3


class PostLikeList(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("post_id", type=int, required=True)
        self.get_parser.add_argument("count", type=int, required=True)
        self.get_parser.add_argument("offset", type=int, required=True)

    @auth_reqd
    @db_session
    def get(self):
        args = self.get_parser.parse_args()
        user = get_user_from_auth_header()

        wanted_post = db.Post.get(id=args.post_id)
        if wanted_post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        if args.count > MAX_FEED_GET_COUNT:
            return format_error_return_v3(ErrorCodes.FEED_GET_COUNT_TOO_HIGH, 400)

        likes = select(l for l in wanted_post.likes) \
            .order_by(db.PostLike.creation_time)

        like_count = likes.count()

        formatted_likes = []

        for like in likes:
            formatted_likes.append(format_userdata_v3(like.user))

        return {
                   "meta": {
                       "count": like_count,
                       "reached_end": len(formatted_likes) < args.count
                   },
                   "like_entries": formatted_likes
               }, 200