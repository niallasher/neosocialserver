from flask_restful import Resource, reqparse
from socialserver.db import db
from pony.orm import db_session
from socialserver.util.auth import get_user_object_from_token_or_abort


class LegacyUserFollows(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Authentication Token", required=True)
        parser.add_argument("username", type=str, help="Username to get follow list for")

        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args["session_token"])

        user = r_user
        if args['username']:
            user = db.User.get(username=args['username'])

        if user is None:
            return {}, 404

        following = []
        # we can't return this directly, since it's a set not a list
        for follow_ent in user.following:
            following.append(follow_ent.following.username)

        return following, 201


class LegacyUserFollowing(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, help="Authentication Token", required=True)
        parser.add_argument("username", type=str, help="Username to get follow list for")

        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args["session_token"])

        user = r_user
        if args['username']:
            user = db.User.get(username=args['username'])

        if user is None:
            return {}, 404

        followers = []
        # we can't return this directly, since it's a set not a list
        for follow_ent in user.followers:
            followers.append(follow_ent.user.username)

        return followers, 201
