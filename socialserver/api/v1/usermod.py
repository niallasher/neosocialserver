from socialserver.util.test import test_db, create_post_with_request, server_address
from socialserver.util.auth import get_user_object_from_token_or_abort, generate_salt, hash_password
from socialserver.util.image import check_image_exists
from socialserver.constants import REGEX_USERNAME_VALID, MAX_PASSWORD_LEN, MIN_PASSWORD_LEN, DISPLAY_NAME_MAX_LEN
from socialserver.db import db
import re
from flask_restful import Resource, reqparse
from pony.orm import db_session, commit


class LegacyUsermod(Resource):

    @db_session
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Session authentication key",
                            required=True)
        parser.add_argument("username", type=str, help="New Username")
        parser.add_argument("password", type=str, help="New Password")
        parser.add_argument("display_name", type=str, help="New Display Name")
        parser.add_argument("avatar_hash", type=str, help="New Avatar Hash (from upload point)")
        parser.add_argument("header_hash", type=str, help="New Header Hash (from upload point)")

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        if args['username'] is not None:
            if not bool(re.match(REGEX_USERNAME_VALID, args['username'])):
                return {}, 400
            user.username = args['username']
            return {}, 201

        if args['password'] is not None:
            if not MIN_PASSWORD_LEN <= len(args['password']) <= MAX_PASSWORD_LEN:
                return {}, 400
            salt = generate_salt()
            hashed_password = hash_password(args['password'], salt)
            user.password_salt = salt
            user.password_hash = hashed_password
            return {}, 201

        if args['display_name'] is not None:
            if not 1 <= len(args['display_name']) <= DISPLAY_NAME_MAX_LEN:
                # again with the minor incompatibilities,
                # but validation is important!
                return {}, 400
            user.display_name = args['display_name']
            return {}, 201

        if args['avatar_hash'] is not None:
            if not check_image_exists(args['avatar_hash']):
                return {}, 404
            image = db.Image.get(identifier=args['avatar_hash'])
            user.profile_pic = image
            return {}, 201

        if args['header_hash'] is not None:
            if not check_image_exists(args['header_hash']):
                return {}, 404
            user.header_pic = db.Image.get(identifier=args['header_hash'])
            return {}, 201

        return {}, 201
