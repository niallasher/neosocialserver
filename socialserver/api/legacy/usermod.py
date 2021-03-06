#  Copyright (c) Niall Asher 2022

from socialserver.util.auth import (
    get_user_object_from_token_or_abort,
    generate_salt,
    hash_password,
)
from socialserver.util.image import check_image_exists
from socialserver.util.config import config
from socialserver.constants import (
    REGEX_USERNAME_VALID,
    MAX_PASSWORD_LEN,
    MIN_PASSWORD_LEN,
    DISPLAY_NAME_MAX_LEN,
)
from socialserver.db import db
import re
from flask_restful import Resource, reqparse
from pony.orm import db_session

LESS_SECURE_PASSWORD_CHANGE_ENABLED = (
    config.legacy_api_interface.enable_less_secure_password_change
)


class LegacyUsermod(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()

        self.post_parser.add_argument(
            "session_token", type=str, help="Session authentication key", required=True
        )
        self.post_parser.add_argument("username", type=str, help="New Username")
        self.post_parser.add_argument("password", type=str, help="New Password")
        self.post_parser.add_argument("display_name", type=str, help="New Display Name")
        self.post_parser.add_argument(
            "avatar_hash", type=str, help="New Avatar Hash (from upload point)"
        )
        self.post_parser.add_argument(
            "header_hash", type=str, help="New Header Hash (from upload point)"
        )

    @db_session
    def post(self):

        args = self.post_parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        if args["username"] is not None:
            if not bool(re.match(REGEX_USERNAME_VALID, args["username"])):
                return {}, 400
            user.username = args["username"]
            return {}, 201

        if args["password"] is not None:
            if LESS_SECURE_PASSWORD_CHANGE_ENABLED:
                if not MIN_PASSWORD_LEN <= len(args["password"]) <= MAX_PASSWORD_LEN:
                    return {}, 400
                salt = generate_salt()
                hashed_password = hash_password(args["password"], salt)
                user.password_salt = salt
                user.password_hash = hashed_password
                return {}, 201
            # return an invalid request if insecure password changes
            # are disabled server side. not good ux, but no alternative!
            return {}, 400

        if args["display_name"] is not None:
            if not 1 <= len(args["display_name"]) <= DISPLAY_NAME_MAX_LEN:
                # again with the minor incompatibilities,
                # but validation is important!
                return {}, 400
            user.display_name = args["display_name"]
            return {}, 201

        if args["avatar_hash"] is not None:
            if not check_image_exists(args["avatar_hash"]):
                return {}, 404
            image = db.Image.get(identifier=args["avatar_hash"])
            user.profile_pic = image
            return {}, 201

        if args["header_hash"] is not None:
            if not check_image_exists(args["header_hash"]):
                return {}, 404
            user.header_pic = db.Image.get(identifier=args["header_hash"])
            return {}, 201

        return {}, 201
