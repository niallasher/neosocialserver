#  Copyright (c) Niall Asher 2022

from datetime import datetime
from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import get_user_from_auth_header, auth_reqd
from socialserver.constants import ErrorCodes, UserNotFoundException
from pony.orm import db_session
from socialserver.util.user import get_user_from_db


class Block(Resource):
    def __init__(self):

        self.post_parser = reqparse.RequestParser()
        # the username to block
        self.post_parser.add_argument("username", type=str, required=True)

        self.delete_parser = reqparse.RequestParser()
        # the username to unblock
        self.delete_parser.add_argument("username", type=str, required=True)

    @db_session
    @auth_reqd
    def post(self):
        args = self.post_parser.parse_args()

        requesting_user_db = get_user_from_auth_header()

        try:
            user_to_follow = get_user_from_db(username=args.username)
        except UserNotFoundException:
            return format_error_return_v3(ErrorCodes.USERNAME_NOT_FOUND, 404)

        if user_to_follow is requesting_user_db:
            return format_error_return_v3(ErrorCodes.CANNOT_BLOCK_SELF, 400)

        existing_follow = db.Block.get(user=requesting_user_db, blocking=user_to_follow)
        if existing_follow is not None:
            return format_error_return_v3(ErrorCodes.BLOCK_ALREADY_EXISTS, 400)

        db.Block(
            user=requesting_user_db,
            blocking=user_to_follow,
            creation_time=datetime.utcnow(),
        )

        return {}, 201

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        requesting_user_db = get_user_from_auth_header()

        try:
            user_to_unblock = get_user_from_db(args.username)
        except UserNotFoundException:
            return format_error_return_v3(ErrorCodes.USERNAME_NOT_FOUND, 404)

        existing_follow = db.Block.get(
            user=requesting_user_db, blocking=user_to_unblock
        )

        if existing_follow is None:
            return format_error_return_v3(ErrorCodes.CANNOT_FIND_BLOCK_ENTRY, 404)

        existing_follow.delete()
        return {}, 204
