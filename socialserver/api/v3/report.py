#  Copyright (c) Niall Asher 2022

from datetime import datetime
from typing import List
from flask_restful import Resource, reqparse
from socialserver.constants import (
    REPORT_SUPPLEMENTARY_INFO_MAX_LEN,
    ErrorCodes,
    ReportReasons,
)
from socialserver.db import db
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from socialserver.util.config import config
from pony.orm import db_session

from socialserver.util.date import format_timestamp_string


class Report(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("post_id", type=int, required=True)

        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("post_id", type=int, required=True)
        # we are going to allow multiple infringement report reasons
        # per post, since we're not allowing a single user to report
        # a post multiple times.
        self.post_parser.add_argument(
            "report_reason", type=int, required=True, action="append"
        )
        self.post_parser.add_argument("supplemental_info", type=str, required=False)

        self.patch_parser = reqparse.RequestParser()
        self.patch_parser.add_argument("report_id", type=int, required=True)
        self.patch_parser.add_argument("mark_active", type=bool, required=True)

    @db_session
    @auth_reqd
    def get(self):
        args = self.get_parser.parse_args()

        user = get_user_from_auth_header()

        if not (user.is_admin or user.is_moderator):
            return format_error_return_v3(ErrorCodes.USER_NOT_MODERATOR_OR_ADMIN, 401)

        wanted_post = db.Post.get(id=args.post_id)
        if wanted_post is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        reports = []
        for r in wanted_post.reports:
            reports.append(
                {
                    "creation_time": format_timestamp_string(r.creation_time),
                    # none represents a deleted account here,
                    # since the relationship will be null
                    "reporter": r.reporter.username or None,
                    "report_info": {
                        "active": r.active,
                        "report_reasons": r.report_reason,
                        "supplementary_info": r.supplementary_info or None,
                    },
                }
            )

        return reports, 201

    @db_session
    @auth_reqd
    def post(self):
        args = self.post_parser.parse_args()

        reporting_user_db = get_user_from_auth_header()

        post_to_be_reported = db.Post.get(id=args.post_id)
        if post_to_be_reported is None:
            return format_error_return_v3(ErrorCodes.POST_NOT_FOUND, 404)

        post_belongs_to_user = post_to_be_reported in reporting_user_db.posts
        if post_belongs_to_user:
            return format_error_return_v3(ErrorCodes.CANNOT_REPORT_OWN_POST, 400)

        existing_report = db.PostReport.get(
            reporter=reporting_user_db, post=post_to_be_reported
        )
        if existing_report is not None:
            # this is supposed to be a spam prevention thing;
            # if failures are silent, and clients don't know,
            # the user won't make new accounts to spam a post. (theoretically)
            # doesn't do much good if the user has read this code lol
            if config.posts.silent_fail_on_double_report:
                return {}, 201
            else:
                return format_error_return_v3(ErrorCodes.POST_ALREADY_REPORTED, 400)

        # append turns the args into an array, that is appended
        # to with each duplicate, hence it being a list
        post_report_reasons: List[int] = args["report_reason"]
        # chuck out any invalid report reasons.
        # we should only see these if people are messing with the api
        # and sending weird values, or some out of date client has an
        # outdated list of report reasons.
        for reason in post_report_reasons:
            if reason not in [e.value for e in ReportReasons]:
                return format_error_return_v3(ErrorCodes.POST_REPORT_REASON_INVALID, 400)

        if args["supplemental_info"] is not None:
            if len(args["supplemental_info"]) > REPORT_SUPPLEMENTARY_INFO_MAX_LEN:
                return format_error_return_v3(ErrorCodes.POST_REPORT_SUPPLEMENTAL_INFO_TOO_LONG, 400)

        db.PostReport(
            active=True,
            reporter=reporting_user_db,
            post=post_to_be_reported,
            creation_time=datetime.utcnow(),
            report_reason=post_report_reasons,
            supplementary_info=args.supplemental_info
            if args.supplemental_info is not None
            else "",
        )

        return {}, 201

    @db_session
    @auth_reqd
    def patch(self):
        args = self.patch_parser.parse_args()

        modifying_user_db = get_user_from_auth_header()

        # only a moderator or admin should be able to influence this
        if True not in [modifying_user_db.is_moderator, modifying_user_db.is_admin]:
            return format_error_return_v3(ErrorCodes.USER_NOT_MODERATOR_OR_ADMIN, 403)

        existing_report = db.PostReport.get(id=args["report_id"])
        if existing_report is None:
            return format_error_return_v3(ErrorCodes.REPORT_NOT_FOUND, 404)

        existing_report.active = args.mark_active

        return {"active": args.mark_active}, 201
