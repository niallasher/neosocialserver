#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from pony.orm import db_session
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.constants import BIO_MAX_LEN
from socialserver.db import db


class LegacyUserBio(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("username", type=str, required=False, help="Username to get")
        args = parser.parse_args()

        r_user = get_user_object_from_token_or_abort(args['session_token'])

        user = r_user
        if args['username']:
            user = db.User.get(username=args['username'])
        if user is None:
            return {}, 404

        return {
                   "bio": user.bio
               }, 201

    @db_session
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("bio", type=str)

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        # we **do not** want to check if it's none:
        # legacy bio removal is done through post instead of delete.
        # why was this choice made?  ¯\_(ツ)_/¯
        if len(user.bio) > BIO_MAX_LEN:
            return {}, 400

        user.bio = args['bio']

        return {}, 201
