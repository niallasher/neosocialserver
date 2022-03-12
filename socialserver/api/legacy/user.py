#  Copyright (c) Niall Asher 2022

from datetime import datetime
import re
from pony.orm import db_session
from socialserver.db import db
from socialserver.util.image import get_image_data_url_legacy
from socialserver.util.config import config
from socialserver.constants import (
    DISPLAY_NAME_MAX_LEN,
    MAX_PASSWORD_LEN,
    MIN_PASSWORD_LEN,
    REGEX_USERNAME_VALID,
    LegacyErrorCodes,
    AccountAttributes,
    ImageTypes,
)
from socialserver.util.auth import (
    generate_salt,
    hash_password,
    verify_password_valid,
    get_user_object_from_token_or_abort,
)
from flask_restful import Resource, reqparse


class LegacyUser(Resource):
    @db_session
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            "session_token", type=str, help="Session authentication key", required=True
        )
        parser.add_argument("username", type=str, help="username to get")
        parser.add_argument(
            "disable_include_images",
            type=str,
            help="Set to not include images in the returned data.",
        )
        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args["session_token"])
        if r_user is None:
            return {"err": LegacyErrorCodes.TOKEN_INVALID.value}, 401

        user = r_user
        if args["username"]:
            user = db.User.get(username=args["username"])
            if user is None:
                return {}, 404
        else:
            user = r_user

        if args["disable_include_images"] is None:
            include_images = True
        else:
            include_images = False

        header_data = ""
        avatar_data = ""

        # TODO: fix this up once there are default images to send back!
        if not args["disable_include_images"]:

            if user.header_pic is None:
                header_data = ""
            else:
                header_data = get_image_data_url_legacy(
                    user.header_pic.identifier, ImageTypes.HEADER
                )

            if user.profile_pic is None:
                avatar_data = ""
            else:
                avatar_data = get_image_data_url_legacy(
                    user.profile_pic.identifier, ImageTypes.PROFILE_PICTURE_LARGE
                )

        user_owns_page = r_user == user
        follower_count = len(user.followers)
        following_count = len(user.following)
        following_user = db.Follow.get(user=r_user, following=user) is not None
        is_blocked = db.Block.get(user=r_user, blocking=user) is not None

        return {
                   "displayName": user.display_name,
                   "username": user.username,
                   "headerData": header_data,
                   "avatarData": avatar_data,
                   "isVerified": user.is_verified,
                   "isAdmin": user.is_admin,
                   "isModerator": user.is_moderator,
                   "isOwnPage": user_owns_page,
                   "isEarlyAdopter": AccountAttributes.OG.value in user.account_attributes,
                   "followerCount": follower_count,
                   "followingCount": following_count,
                   "isFollowing": following_user,
                   "isBlocked": is_blocked,
               }, 200

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()

        parser.add_argument(
            "session_token", type=str, help="Session authentication key", required=True
        )
        parser.add_argument("password", type=str, help="password to delete user")

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args["session_token"])

        # in any normal circumstance, this would just be a required
        # argument, but recreating the 1.x - 2.x interfaces seems to
        # lend itself to a lot of abnormal circumstances, i'm afraid.
        if args.password == "":
            return {}, 401

        if verify_password_valid(
                args["password"], user.password_salt, user.password_hash
        ):
            user.delete()
            return {}, 201
        else:
            return {}, 401

    @db_session
    def post(self):

        # we don't really have a better error to launch back here,
        # since the old client doesn't support any others
        if not config.legacy_api_interface.signup_enabled:
            return {"err": LegacyErrorCodes.GENERIC_SERVER_ERROR.value}, 400

        # not compatible with the v1 client, and i'm not sure if it
        # can be comfortably reconciled. will investigate, but for now,
        # return early.
        if config.auth.registration.approval_required:
            return {"err": LegacyErrorCodes.GENERIC_SERVER_ERROR.value}, 400

        parser = reqparse.RequestParser()

        parser.add_argument(
            "username", type=str, help="Username for created account", required=True
        )
        parser.add_argument(
            "password", type=str, help="Password for created account", required=True
        )
        parser.add_argument(
            "display_name",
            type=str,
            help="Display name for created account",
            required=True,
        )
        # parser.add_argument('invite_code', type=str, help="Invite code to socialshare", required=False)

        args = parser.parse_args()

        # NOTE: this isn't *exactly* compatible, since the old version had basically no validation
        # for usernames, but we've gotta diverge a bit here since the new server does
        if not bool(re.match(REGEX_USERNAME_VALID, args["username"])):
            # yep, no error again :)
            # i feel unclean
            return {}, 400

        # this also isn't *exactly* compatible.........  ¯\_(ツ)_/¯
        password_ok = MIN_PASSWORD_LEN <= len(args["password"]) <= MAX_PASSWORD_LEN
        if not password_ok:
            return {}, 400

        # or this. the old server was very lax about validation, huh?
        if len(args["display_name"]) > DISPLAY_NAME_MAX_LEN:
            return {}, 400

        existing_user = db.User.get(username=args["username"])
        if existing_user is not None:
            return {"err": LegacyErrorCodes.USERNAME_TAKEN.value}, 400

        salt = generate_salt()
        password = hash_password(args["password"], salt)

        db.User(
            display_name=args["display_name"],
            username=args["username"],
            password_hash=password,
            password_salt=salt,
            creation_time=datetime.utcnow(),
            # legacy accounts are currently defined as those
            # migrated from the old service, due to possible changes
            # any new account should be indistinguishable regardless
            # of if it was made through back-compat
            is_legacy_account=False,
            account_attributes=[],
            bio="",
            # we've already returned if approval was required...
            account_approved=True,
        )

        return {}, 201
