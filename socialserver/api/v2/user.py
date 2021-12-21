from datetime import datetime
import re
from socialserver.db import db as prod_db
from flask_restful import Resource, reqparse
from socialserver.constants import BIO_MAX_LEN, DISPLAY_NAME_MAX_LEN, MAX_PASSWORD_LEN, MIN_PASSWORD_LEN, ErrorCodes, \
    REGEX_USERNAME_VALID
from socialserver.util.auth import generate_salt, get_username_from_token, hash_password, verify_password_valid
from pony.orm import db_session
from socialserver.util.config import config

db = prod_db


class UserInfo(Resource):

    @db_session
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args()

        # in the future, we might not require sign-in for read only access
        # to some parts, but for now we do.
        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        wanted_user = db.User.get(username=args['username'])
        if wanted_user is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        pfp = None
        header = None

        if wanted_user.profile_pic is not None:
            pfp = wanted_user.profile_pic.identifier

        if wanted_user.header_pic is not None:
            header = wanted_user.header_pic.identifier

        return {
                   "username": wanted_user.username,
                   "display_name": wanted_user.display_name,
                   "birthday": wanted_user.birthday,
                   "account_attributes": wanted_user.account_attributes,
                   "bio": wanted_user.bio,
                   "follower_count": wanted_user.followers.count(),
                   "following_count": wanted_user.following.count(),
                   "profile_picture": pfp,
                   "header": header
               }, 200


class User(Resource):

    @db_session
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('display_name', type=str, required=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('bio', type=str)
        # birthday is unimplemented for now.
        # this will have to be turned into a datetime.date,
        # and there are a lot of considerations. probably
        # a feature to do *after* everything else works!
        # parser.add_argument('birthday', type=str)
        args = parser.parse_args()

        # all this validation should be done clientside,
        # but we're replicating here in case of an error on the client
        # or a bad actor. hence, the ux doesn't have to be amazing,
        # and it doesn't really matter if we don't check everything
        # before exiting. we just report the first issue we find and
        # return.

        # usernames can only have a-z, A-Z, 0-9 or _, and must be between 1 and 20 chars
        if not bool(re.match(REGEX_USERNAME_VALID, args['username'])):
            return {"error": ErrorCodes.USERNAME_INVALID.value}, 400

        existing_user = db.User.get(username=args['username'])
        print(existing_user)
        if existing_user is not None:
            return {"error": ErrorCodes.USERNAME_TAKEN.value}, 400

        if args['bio'] is not None and len(args['bio']) >= BIO_MAX_LEN:
            return {"error": ErrorCodes.BIO_NON_CONFORMING.value}, 400

        if len(args['display_name']) >= DISPLAY_NAME_MAX_LEN:
            return {"error": ErrorCodes.DISPLAY_NAME_NON_CONFORMING.value}, 400

        password_ok = len(args['password']) >= MIN_PASSWORD_LEN and len(
            args['password']) <= MAX_PASSWORD_LEN
        if not password_ok:
            return {"error": ErrorCodes.PASSWORD_NON_CONFORMING.value}, 400

        salt = generate_salt()
        password = hash_password(args['password'], salt)

        db.User(
            display_name=args['display_name'],
            username=args['username'],
            password_hash=password,
            password_salt=salt,
            creation_time=datetime.now(),
            is_legacy_account=False,
            account_attributes=[],
            bio=args['bio'] if args['bio'] is not None else "",
            account_approved=True if config.auth.registration.approval_required is False else False
        )

        return {"needs_approval": config.auth.registration.approval_required}, 201

    @db_session
    def patch(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('display_name', type=str, required=False)
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('bio', type=str, required=False)
        parser.add_argument('profile_pic_ref', type=str, required=False)
        parser.add_argument('header_pic_ref', type=str, required=False)

        args = parser.parse_args()

        username = get_username_from_token(args['access_token'])
        user = db.User.get(username=username)

        if args['display_name'] is not None:
            if len(args['display_name']) > DISPLAY_NAME_MAX_LEN:
                return {"error": ErrorCodes.DISPLAY_NAME_NON_CONFORMING.value}, 400
            user.display_name = args['display_name']
            return {"display_name": args['display_name']}, 201

        if args['username'] is not None:
            if not bool(re.match(REGEX_USERNAME_VALID, args['username'])):
                return {"error": ErrorCodes.USERNAME_INVALID.value}, 400
            if db.User.get(username=args['username']) is not None:
                return {"error": ErrorCodes.USERNAME_TAKEN.value}, 400
            user.username = args['username']
            return {"username": args['username']}

        if args['bio'] is not None:
            if len(args['bio']) > BIO_MAX_LEN:
                return {"error": ErrorCodes.BIO_NON_CONFORMING.value}, 400
            user.bio = args['bio']
            # NOTE: not sure; should we return new bio? client might want to cache it.
            # they could always just keep it from when it was entered, I don't know.
            return {}, 201

        if args['profile_pic_ref'] is not None:
            existing_image = db.Image.get(identifier=args['profile_pic_ref'])
            if existing_image is None:
                return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404
            user.profile_pic = existing_image
            return {"profile_pic_ref": args['profile_pic_ref']}, 201

        if args['header_pic_ref'] is not None:
            existing_image = db.Image.get(identifier=args['header_pic_ref'])
            if existing_image is None:
                return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404
            user.header_pic = existing_image
            return {"header_pic_ref": args['header_pic_ref']}, 201

        return {"error": ErrorCodes.USER_MODIFICATION_NO_OPTIONS_GIVEN.value}, 400

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        print(db.select("select * from User"))
        print(db.select("select * from UserSession"))

        requesting_username = get_username_from_token(args['access_token'])
        if requesting_username is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        requesting_user = db.User.get(username=requesting_username)

        if not verify_password_valid(args['password'],
                                     requesting_user.password_salt,
                                     requesting_user.password_hash):
            return {"error": ErrorCodes.INCORRECT_PASSWORD.value}, 401

        requesting_user.delete()
        return {}, 200
