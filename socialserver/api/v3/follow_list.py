#  Copyright (c) Niall Asher 2022
from socialserver.util.api.v3.data_format import format_userdata_v3
from socialserver.util.api.v3.follow_info import get_follow_info_for_user
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from socialserver.constants import ErrorCodes, MAX_FEED_GET_COUNT, UserNotFoundException, FollowListSortTypes, \
    FollowListListTypes
from pony.orm import db_session, select, desc
from flask_restful import Resource, reqparse

from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.user import get_user_from_db


class FollowerList(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("sort_type", type=int, required=True)
        # we assume the user want's information about themselves if they don't specify a username
        self.get_parser.add_argument("username", type=str, required=False)
        self.get_parser.add_argument("count", type=int, required=True)
        self.get_parser.add_argument("offset", type=int, required=True)

    @auth_reqd
    @db_session
    def get(self):
        args = self.get_parser.parse_args()
        user = get_user_from_auth_header()

        wanted_user = user
        if args.username is not None:
            try:
                wanted_user = get_user_from_db(args.username)
            except UserNotFoundException:
                return format_error_return_v3(ErrorCodes.USERNAME_NOT_FOUND, 404)

        if args.count > MAX_FEED_GET_COUNT:
            return format_error_return_v3(ErrorCodes.FEED_GET_COUNT_TOO_HIGH, 400)

        return get_follow_info_for_user(wanted_user, count=args.count, offset=args.offset, sort_type=args.sort_type,
                                        list_type=FollowListListTypes.FOLLOWERS)


class FollowingList(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("sort_type", type=int, required=True)
        # we assume the user want's information about themselves if they don't specify a username
        self.get_parser.add_argument("username", type=str, required=False)
        self.get_parser.add_argument("count", type=int, required=True)
        self.get_parser.add_argument("offset", type=int, required=True)

    @auth_reqd
    @db_session
    def get(self):
        args = self.get_parser.parse_args()
        user = get_user_from_auth_header()

        wanted_user = user
        if args.username is not None:
            try:
                wanted_user = get_user_from_db(args.username)
            except UserNotFoundException:
                return format_error_return_v3(ErrorCodes.USERNAME_NOT_FOUND, 404)

        if args.count > MAX_FEED_GET_COUNT:
            return format_error_return_v3(ErrorCodes.FEED_GET_COUNT_TOO_HIGH, 400)

        return get_follow_info_for_user(wanted_user, count=args.count, offset=args.offset, sort_type=args.sort_type,
                                        list_type=FollowListListTypes.FOLLOWING)
