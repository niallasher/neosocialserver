from datetime import datetime
import re
from socialserver.db import DbUser
from flask_restful import Resource, reqparse
from socialserver.constants import BIO_MAX_LEN, DISPLAY_NAME_MAX_LEN, MAX_PASSWORD_LEN, MIN_PASSWORD_LEN, USERNAME_MAX_LEN, ErrorCodes, REGEX_USERNAME_VALID
from socialserver.util.auth import generate_salt, get_username_from_token, hash_password, verify_password_valid
from pony.orm import db_session


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

        wanted_user = DbUser.get(username=args['username'])
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
            "bio":  wanted_user.bio,
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
        # or a bad actor. hence the ux doesn't have to be amazing,
        # and it doesn't really matter if we don't check everything
        # before exiting. we just report the first issue we find and
        # return.

        # usernames can only have a-z, A-Z, 0-9 or _, and must be between 1 and 20 chars
        if not bool(re.match(REGEX_USERNAME_VALID, args['username'])):
            return {"error": ErrorCodes.USERNAME_INVALID.value}, 400

        existing_user = DbUser.get(username=args['username'])
        if existing_user is not None:
            return {"error": ErrorCodes.USERNAME_TAKEN.value}, 400

        if args['bio'] != None and len(args['bio']) >= BIO_MAX_LEN:
            return {"error": ErrorCodes.BIO_NON_CONFORMING.value}, 400

        if len(args['display_name']) >= DISPLAY_NAME_MAX_LEN:
            return {"error": ErrorCodes.DISPLAY_NAME_NON_CONFORMING.value}, 400

        password_ok = len(args['password']) >= MIN_PASSWORD_LEN and len(
            args['password']) <= MAX_PASSWORD_LEN
        if not password_ok:
            return {"error": ErrorCodes.PASSWORD_NON_CONFORMING.value}, 400

        salt = generate_salt()
        password = hash_password(args['password'], salt)

        DbUser(
            display_name=args['display_name'],
            username=args['username'],
            password_hash=password,
            password_salt=salt,
            creation_time=datetime.now(),
            is_legacy_account=False,
            account_attributes=[],
            bio=args['bio'] if args['bio'] != None else ""
        )

        return {}, 201

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        requesting_user = get_username_from_token(args['access_token'])
        if requesting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        if not verify_password_valid(args['password'],
                                     requesting_user.password_salt,
                                     requesting_user.password_hash):
            return {"error": ErrorCodes.INCORRECT_PASSWORD.value}, 401

        requesting_user.delete()
        return {}, 200
