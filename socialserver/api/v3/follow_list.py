#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from socialserver.constants import ErrorCodes, FollowListSortTypes, MAX_FEED_GET_COUNT, FollowListListTypes
from socialserver.util.api.v3.data_format import format_userdata_v3
from pony.orm import db_session, select, desc
from flask_restful import Resource, reqparse


class FollowList(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        # one of FollowListSortTypes
        self.get_parser.add_argument("sort_type", type=int, required=True)
        # if not present, we want to get the current user's info from the auth token.
        self.get_parser.add_argument("username", type=str, required=False)
        self.get_parser.add_argument("count", type=int, required=True)
        self.get_parser.add_argument("offset", type=int, required=True)
        # one of FollowListListTypes
        self.get_parser.add_argument("list_type", type=int, required=True)

    @db_session
    def get(self):
        args = self.get_parser.parse_args()
        user = get_user_from_auth_header()

        if args["username"] is None:
            wanted_user = user
        else:
            wanted_user = db.User.get(username=args["username"])
            if wanted_user is None:
                return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if args["count"] > MAX_FEED_GET_COUNT:
            return {"error": ErrorCodes.FEED_GET_COUNT_TOO_HIGH.value}, 400

        if args['list_type'] == FollowListListTypes.FOLLOWERS.value:
            query = select(fe for fe in wanted_user.followers)
        elif args['list_type'] == FollowListListTypes.FOLLOWING.value:
            query = select(fe for fe in wanted_user.following)
        else:
            return {}, 400

        is_following_list = args['list_type'] == FollowListListTypes.FOLLOWING.value

        count = query.count()

        # sort the query.
        # it's a bit messy, but honestly it works (it doesn't), and I don't want to deal
        # with pony throwing me a decompilation exception whenever I try an alternate
        # solution.
        if args["sort_type"] == FollowListSortTypes.USERNAME_ALPHABETICAL.value:
            return {"error": ErrorCodes.OPTION_UNIMPLEMENTED.value}, 500
        elif args["sort_type"] == FollowListSortTypes.DISPLAY_NAME_ALPHABETICAL.value:
            return {"error": ErrorCodes.OPTION_UNIMPLEMENTED.value}, 500
        # yep, it's inverted. yep, that makes it give the right result.
        elif args["sort_type"] == FollowListSortTypes.AGE_ASCENDING.value:
            query = query.order_by(lambda fe: desc(fe.creation_time))
        elif args["sort_type"] == FollowListSortTypes.AGE_DESCENDING.value:
            query = query.order_by(lambda fe: fe.creation_time)
        else:
            return {"error": ErrorCodes.INVALID_SORT_TYPE.value}, 400

        # and cut out what we don't need
        query = query.limit(args['count'], offset=args['offset'])  # convert to a list

        user_objects = []
        if is_following_list:
            for fe in query:
                user_objects.append(format_userdata_v3(
                    fe.following, user
                ))
        else:
            for fe in query:
                user_objects.append(format_userdata_v3(
                    fe.user, user
                ))

        return {
                   "meta": {
                       "count": count,
                       "reached_end": len(user_objects) < args['count']
                   },
                   "follow_entries": user_objects
               }, 200
