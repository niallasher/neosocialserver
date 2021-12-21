from datetime import datetime
from typing import List
from flask_restful import Resource, reqparse
from socialserver.constants import REPORT_SUPPLEMENTARY_INFO_MAX_LEN, ErrorCodes, ReportReasons
from socialserver.db import db
from socialserver.util.auth import get_username_from_token
from socialserver.util.config import config
from pony.orm import db_session


class Report(Resource):

    @db_session
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument("access_token", type=str, required=True)
        parser.add_argument("post_id", type=int, required=True)
        # we are going to allow multiple infringement report reasons
        # per post, since we're not allowing a single user to report
        # a post multiple times.
        parser.add_argument("report_reason", type=int,
                            required=True, action="append")
        parser.add_argument("supplemental_info", type=str, required=False)
        args = parser.parse_args()

        reporting_user: str = get_username_from_token(args['access_token'])
        if reporting_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401
        reporting_user_db = db.User.get(username=reporting_user)

        post_to_be_reported = db.Post.get(id=args['post_id'])
        if post_to_be_reported is None:
            return {"error": ErrorCodes.POST_NOT_FOUND.value}, 404

        existing_report = db.PostReport.get(
            reporter=reporting_user_db,
            post=post_to_be_reported
        )
        if existing_report is not None:
            # this is supposed to be a spam prevention thing;
            # if failures are silent, and clients don't know,
            # the user won't make new accounts to spam a post. (theoretically)
            # doesn't do much good if the user has read this code lol
            if config.posts.silent_fail_on_double_report:
                return {}, 201
            else:
                return {"error": ErrorCodes.POST_ALREADY_REPORTED}, 400

        # append turns the args into an array, that is appended
        # to with each duplicate, hence it being a list
        post_report_reasons: List[int] = args['report_reason']
        # chuck out any invalid report reasons.
        # we should only see these if people are messing with the api
        # and sending weird values, or some out of date client has an
        # outdated list of report reasons.
        for reason in post_report_reasons:
            if reason not in [e.value for e in ReportReasons]:
                return {"error": ErrorCodes.POST_REPORT_REASON_INVALID.value}, 400

        if args['supplemental_info'] is not None:
            if len(args['supplemental_info']) > REPORT_SUPPLEMENTARY_INFO_MAX_LEN:
                return {"error": ErrorCodes.POST_REPORT_SUPPLEMENTAL_INFO_TOO_LONG.value}, 400

        db.PostReport(
            active=True,
            reporter=reporting_user_db,
            post=post_to_be_reported,
            creation_time=datetime.now(),
            report_reason=post_report_reasons,
            supplementary_info=args['supplemental_info'] if args['supplemental_info'] is not None else ""
        )

        return {}, 201

    @db_session
    def patch(self):

        parser = reqparse.RequestParser()
        parser.add_argument("access_token", type=str, required=True)
        parser.add_argument("report_id", type=int, required=True)
        parser.add_argument("mark_active", type=bool, required=True)
        args = parser.parse_args()

        modifying_user = get_username_from_token(args['access_token'])
        if modifying_user is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        modifying_user_db = db.User.get(username=modifying_user)

        # only a moderator or admin should be able to influence this
        if True not in [modifying_user_db.is_moderator, modifying_user_db.is_admin]:
            return {"error": ErrorCodes.USER_NOT_MODERATOR_OR_ADMIN.value}, 403

        existing_report = db.PostReport.get(
            id=args['report_id']
        )
        if existing_report is None:
            return {"error": ErrorCodes.REPORT_NOT_FOUND.value}, 404

        existing_report.active = args['mark_active']

        return {"active": args['mark_active']}, 201
