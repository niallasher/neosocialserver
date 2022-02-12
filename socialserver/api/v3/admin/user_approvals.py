#  Copyright (c) Niall Asher 2022

from socialserver.db import db
from socialserver.util.auth import admin_reqd, get_user_from_auth_header
from flask_restful import Resource, reqparse
from socialserver.constants import ApprovalSortTypes, ErrorCodes
from pony.orm import db_session, select, desc, count


class UserApprovals(Resource):

    @db_session
    @admin_reqd
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('count', type=int, required=True)
        parser.add_argument('offset', type=int, required=True)
        # one of ApprovalSortTypes
        parser.add_argument('sort', type=int, required=True)
        # filters only usernames right now
        parser.add_argument('filter', type=str, required=False)

        args = parser.parse_args()

        unapproved_users = select(user for user in db.User
                                  if user.account_approved is False)

        if args['sort'] == ApprovalSortTypes.CREATION_TIME_ASCENDING.value:
            unapproved_users = unapproved_users.sort_by(db.User.creation_time)
        elif args['sort'] == ApprovalSortTypes.CREATION_TIME_DESCENDING.value:
            unapproved_users = unapproved_users.sort_by(desc(db.User.creation_time))
        elif args['sort'] == ApprovalSortTypes.USERNAME_ALPHABETICAL.value:
            unapproved_users = unapproved_users.sort_by(db.User.username)
        elif args['sort'] == ApprovalSortTypes.DISPLAY_NAME_ALPHABETICAL.value:
            unapproved_users = unapproved_users.sort_by(db.User.display_name)
        else:
            return {"error": ErrorCodes.INVALID_SORT_TYPE.value}, 400

        if args['filter']:
            unapproved_users = unapproved_users.filter(lambda user: args['filter'].strip() in user.username)

        # we limit down here, since you can't filter or sort a query once it's been limited in ponyorm.
        # why this is, I don't know, but I'd assume there's a good reason for it.
        unapproved_users = unapproved_users.limit(args['count'], offset=args['offset'])

        users_formatted = []
        for user in unapproved_users:
            users_formatted.append(
                {
                    "username": user.username,
                    "creation_time": user.creation_time.timestamp()
                }
            )

        return {
                   "meta": {
                       "reached_end": len(users_formatted) < args['count']
                   },
                   "users": users_formatted
               }, 201

    @db_session
    @admin_reqd
    # only a partial mod to a resource, so it's a patch request.
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True)
        args = parser.parse_args()

        user = db.User.get(username=args['username'])
        if user is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if user.account_approved:
            return {"error": ErrorCodes.USER_ALREADY_APPROVED.value}, 400

        user.account_approved = True
        return {}, 200

    @db_session
    @admin_reqd
    # obliterate a user completely (aka reject them, deleting the unapproved account)
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True)
        args = parser.parse_args()

        user = db.User.get(username=args['username'])
        if user is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if user.account_approved:
            return {"error": ErrorCodes.USER_ALREADY_APPROVED.value}, 400

        user.delete()
        return {}, 200
