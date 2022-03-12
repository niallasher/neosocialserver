#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from pony.orm import db_session
from socialserver.constants import LegacyErrorCodes
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.db import db


class LegacyAdminDeletePost(Resource):
    @db_session
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "session_token", type=str, required=True, help="Authentication Token"
        )
        parser.add_argument(
            "post_id", type=int, required=True, help="Post ID to admin delete"
        )
        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        if not user.is_admin:
            return {"err": LegacyErrorCodes.USER_NOT_ADMIN.value}, 401

        post = db.Post.get(id=args["post_id"])
        if post is None:
            return {"err": LegacyErrorCodes.POST_NOT_FOUND.value}, 404

        # cya
        post.delete()
        return {}, 201
