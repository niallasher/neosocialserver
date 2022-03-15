#  Copyright (c) Niall Asher 2022

from datetime import datetime
from socialserver.db import db
from flask_restful import Resource, reqparse
from pony.orm import db_session
from flask import request
from socialserver.constants import ErrorCodes
from socialserver.util.auth import (
    generate_key,
    get_ip_from_request,
    hash_plaintext_sha256,
    verify_password_valid,
    auth_reqd,
    get_user_from_auth_header,
    check_totp_valid,
    TotpExpendedException,
    TotpInvalidException,
)
from socialserver.util.config import config
from user_agents import parse as ua_parse


class UserSession(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("username", type=str, required=True)
        self.post_parser.add_argument("password", type=str, required=True)
        # Only needed if TOTP is enabled!
        self.post_parser.add_argument("totp", type=str, required=False)

    @db_session
    @auth_reqd
    def get(self):

        session = db.UserSession.get(
            access_token_hash=hash_plaintext_sha256(
                request.headers["Authorization"].split(" ")[1]
            )
        )

        if session is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        return (
            {
                "owner": session.user.username,
                "current_ip": get_ip_from_request(),
                "creation_ip": session.creation_ip,
                "creation_time": session.creation_time.timestamp(),
                "current_server_time": datetime.utcnow().timestamp(),
                "last_access_time": session.last_access_time.timestamp(),
                "user_agent": session.user_agent,
            },
            200,
        )

    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        user = db.User.get(username=args["username"])
        if user is None:
            return {"error": ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if not verify_password_valid(
            args["password"], user.password_salt, user.password_hash
        ):
            return {"error": ErrorCodes.INCORRECT_PASSWORD.value}, 401

        if config.auth.registration.approval_required:
            if user.account_approved is not True:
                return {"error": ErrorCodes.ACCOUNT_NOT_APPROVED.value}, 401

        # if the user has totp, and hasn't specified one, send back an error
        # telling the client they'll need to supply it.
        if user.totp is not None and user.totp.confirmed:
            # default value for the unspecified arg is an
            # empty string, hence this and not args['totp'] is None!
            if args["totp"] == "" or args["totp"] is None:
                return {"error": ErrorCodes.TOTP_REQUIRED.value}, 400

            try:
                check_totp_valid(args["totp"], user)
            except TotpExpendedException:
                return {"error": ErrorCodes.TOTP_EXPENDED.value}, 401
            except TotpInvalidException:
                return {"error": ErrorCodes.TOTP_INCORRECT.value}, 401

        secret = generate_key()

        db.UserSession(
            user=user,
            access_token_hash=secret.hash,
            creation_ip=get_ip_from_request(),
            creation_time=datetime.utcnow(),
            last_access_time=datetime.utcnow(),
            user_agent=request.headers.get("User-Agent"),
        )

        return {"access_token": secret.key}, 200

    @db_session
    @auth_reqd
    def delete(self):

        session = db.UserSession.get(
            access_token_hash=hash_plaintext_sha256(
                request.headers["Authorization"].split(" ")[1]
            )
        )
        if session is None:
            return {"error": ErrorCodes.TOKEN_INVALID.value}, 401

        session.delete()
        return {}, 201


class UserSessionList(Resource):
    """
    return a list of the users sessions, with basic info.
    """

    @db_session
    @auth_reqd
    def get(self):
        sessions = []
        user = get_user_from_auth_header()

        for s in user.sessions:
            user_agent = ua_parse(s.user_agent)
            sessions.append(
                {
                    "creation_ip": s.creation_ip,
                    "creation_time": s.creation_time.timestamp(),
                    "last_access_time": s.last_access_time.timestamp(),
                    # current = true if this is the session the user used to request the list
                    # this is just to make it easy for a client to add a tag saying something
                    # like [THIS DEVICE] to an entry in the list of sessions
                    "current": s.access_token_hash
                    == hash_plaintext_sha256(
                        request.headers["Authorization"].split(" ")[1]
                    ),
                    # the device that created the session, this should just about always be the
                    # same device that created it anyway, unless you've been reusing access tokens(?)
                    # or have used a backup program or smth to copy ur data
                    "device_info": {
                        # user_agent.os is an array containing the OS first,
                        # followed by version info. we just want the os name.
                        "operating_system": user_agent.os[0],
                        "device": {
                            "brand": user_agent.device.brand,
                            "model": user_agent.device.model,
                            # same as user_agent.os
                            "browser": user_agent.browser[0],
                        },
                    },
                }
            )

        return sessions, 200
