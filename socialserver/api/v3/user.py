#  Copyright (c) Niall Asher 2022

from datetime import datetime
import re
from socialserver.db import db
from flask_restful import Resource, reqparse
from socialserver.constants import (
    BIO_MAX_LEN,
    DISPLAY_NAME_MAX_LEN,
    MAX_PASSWORD_LEN,
    MIN_PASSWORD_LEN,
    ErrorCodes,
    REGEX_USERNAME_VALID, UserNotFoundException,
)
from socialserver.util.api.v3.data_format import format_userdata_v3
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import (
    generate_salt,
    hash_password,
    verify_password_valid,
    auth_reqd,
    get_user_from_auth_header,
)
from pony.orm import db_session
from socialserver.util.config import config
from socialserver.util.user import get_user_from_db


class UserInfo(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("username", type=str, required=False)

    @db_session
    @auth_reqd
    def get(self):

        args = self.get_parser.parse_args()

        if args.username is None:
            wanted_user = get_user_from_auth_header()
        else:
            try:
                wanted_user = get_user_from_db(username=args.username)
            except UserNotFoundException:
                return format_error_return_v3(ErrorCodes.USERNAME_NOT_FOUND, 404)

        return (
            format_userdata_v3(
                wanted_user,
                include_header=True,
                include_bio=True,
                include_follower_info=True,
            ),
            200,
        )


class User(Resource):
    def __init__(self):

        self.patch_parser = reqparse.RequestParser()
        self.patch_parser.add_argument("display_name", type=str, required=False)
        self.patch_parser.add_argument("username", type=str, required=False)
        self.patch_parser.add_argument("bio", type=str, required=False)
        self.patch_parser.add_argument("profile_pic_ref", type=str, required=False)
        self.patch_parser.add_argument("header_pic_ref", type=str, required=False)

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("display_name", type=str, required=True)
        self.post_parser.add_argument("username", type=str, required=True)
        self.post_parser.add_argument("password", type=str, required=True)
        self.post_parser.add_argument("bio", type=str)

        self.delete_parser = reqparse.RequestParser()
        self.delete_parser.add_argument("password", type=str, required=True)

    @db_session
    def post(self):
        # birthday is unimplemented for now.
        # this will have to be turned into a datetime.date,
        # and there are a lot of considerations. probably
        # a feature to do *after* everything else works!
        # parser.add_argument('birthday', type=str)
        args = self.post_parser.parse_args()

        # all this validation should be done clientside,
        # but we're replicating here in case of an error on the client
        # or a bad actor. hence, the ux doesn't have to be amazing,
        # and it doesn't really matter if we don't check everything
        # before exiting. we just report the first issue we find and
        # return.

        # usernames can only have a-z, A-Z, 0-9 or _, and must be between 1 and 20 chars
        if not bool(re.match(REGEX_USERNAME_VALID, args.username)):
            return format_error_return_v3(ErrorCodes.USERNAME_INVALID, 400)

        existing_user = db.User.get(username=args.username)
        if existing_user is not None:
            return format_error_return_v3(ErrorCodes.USERNAME_TAKEN, 400)

        if args.bio is not None and len(args.bio) >= BIO_MAX_LEN:
            return format_error_return_v3(ErrorCodes.BIO_NON_CONFORMING, 400)

        if len(args.display_name) >= DISPLAY_NAME_MAX_LEN:
            return format_error_return_v3(ErrorCodes.DISPLAY_NAME_NON_CONFORMING, 400)

        password_ok = MIN_PASSWORD_LEN <= len(args.password) <= MAX_PASSWORD_LEN
        if not password_ok:
            return format_error_return_v3(ErrorCodes.PASSWORD_NON_CONFORMING, 400)

        salt = generate_salt()
        password = hash_password(args.password, salt)

        db.User(
            display_name=args.display_name,
            username=args.username,
            password_hash=password,
            password_salt=salt,
            creation_time=datetime.utcnow(),
            is_legacy_account=False,
            account_attributes=[],
            bio=args.bio if args.bio is not None else "",
            account_approved=True
            if config.auth.registration.approval_required is False
            else False,
        )

        return {"needs_approval": config.auth.registration.approval_required}, 201

    @db_session
    @auth_reqd
    def patch(self):
        args = self.patch_parser.parse_args()

        user = get_user_from_auth_header()

        if args.display_name is not None:
            if len(args.display_name) > DISPLAY_NAME_MAX_LEN:
                return format_error_return_v3(ErrorCodes.DISPLAY_NAME_NON_CONFORMING, 400)
            user.display_name = args.display_name
            return {"display_name": args.display_name}, 201

        if args.username is not None:
            if not bool(re.match(REGEX_USERNAME_VALID, args.username)):
                return format_error_return_v3(ErrorCodes.USERNAME_INVALID, 400)
            if db.User.get(username=args.username) is not None:
                return format_error_return_v3(ErrorCodes.USERNAME_TAKEN, 400)
            user.username = args.username
            return {"username": args.username}

        if args.bio is not None:
            if len(args.bio) > BIO_MAX_LEN:
                return format_error_return_v3(ErrorCodes.BIO_NON_CONFORMING, 400)
            user.bio = args.bio
            # NOTE: not sure; should we return new bio? client might want to cache it.
            # they could always just keep it from when it was entered, I don't know.
            return {}, 201

        if args.profile_pic_ref is not None:
            existing_image = db.Image.get(identifier=args.profile_pic_ref)
            if existing_image is None:
                return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)
            if existing_image.processed is False:
                return format_error_return_v3(ErrorCodes.IMAGE_NOT_PROCESSED, 404)
            user.profile_pic = existing_image
            return {"profile_pic_ref": args.profile_pic_ref}, 201

        if args.header_pic_ref is not None:
            existing_image = db.Image.get(identifier=args.header_pic_ref)
            if existing_image is None:
                return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)
            if existing_image.processed is False:
                return format_error_return_v3(ErrorCodes.IMAGE_NOT_PROCESSED, 404)
            user.header_pic = existing_image
            return {"header_pic_ref": args.header_pic_ref}, 201

        return format_error_return_v3(ErrorCodes.USER_MODIFICATION_NO_OPTIONS_GIVEN, 400)

    @db_session
    @auth_reqd
    def delete(self):
        args = self.delete_parser.parse_args()

        requesting_user = get_user_from_auth_header()

        if not verify_password_valid(
            args.password,
            requesting_user.password_salt,
            requesting_user.password_hash,
        ):
            return format_error_return_v3(ErrorCodes.INCORRECT_PASSWORD, 401)

        requesting_user.delete()
        return {}, 200
