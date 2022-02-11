from flask_restful import Resource, reqparse
from pony.orm import db_session
from socialserver.db import db
from socialserver.constants import LegacyErrorCodes
from socialserver.util.auth import verify_password_valid, generate_key, get_ip_from_request, hash_plaintext_sha256, \
    check_totp_valid, TotpInvalidException, TotpExpendedException
from flask import request
from datetime import datetime


class LegacyAuthentication(Resource):

    @staticmethod
    def get(self):
        # yep, this is intentional.
        # not sure why this was the case in v1, but
        # we're keeping it since it was.
        return 401

    @db_session
    def post(self):

        # notes for totp implementation:
        # if totp_enabled and no totp, then return
        # {'err': LegacyErrorCodes.TOTP_REQUIRED.value}, 401.
        # if it's invalid:
        # {'err': LegacyErrorCodes.TOTP_INCORRECT.value}, 401
        # v1 will return the totp request even if pw is wrong.

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('totp', type=str, required=False, default=None)  # TODO: this needs to be re-implemented!

        args = parser.parse_args()

        if args.username == '' or args.password == '':
            return {}, 401

        user = db.User.get(username=args['username'])
        if user is None:
            return {"err": LegacyErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if not verify_password_valid(args['password'], user.password_salt, user.password_hash):
            # yes, this is completely the wrong error to return, however,
            # for whatever reason, this was what API v1 did.
            return {"err": LegacyErrorCodes.PASSWORD_DAMAGED.value}, 401

        if user.totp is not None:
            if args['totp'] == "" or args['totp'] is None:
                return {"err": LegacyErrorCodes.TOTP_REQUIRED.value}, 401
            try:
                check_totp_valid(args['totp'], user)
            except TotpInvalidException or TotpExpendedException:
                return {"err": LegacyErrorCodes.TOTP_INCORRECT.value}, 401

        secret = generate_key()

        db.UserSession(
            user=user,
            access_token_hash=secret.hash,
            creation_ip=get_ip_from_request(),
            creation_time=datetime.utcnow(),
            last_access_time=datetime.utcnow(),
            user_agent=request.headers.get("User-Agent")
        )

        return secret.key

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument('session_token', type=str, required=True)

        args = parser.parse_args()

        access_token_hash = hash_plaintext_sha256(args['session_token'])

        session = db.UserSession.get(access_token_hash=access_token_hash)
        if session is None:
            return {}, 401

        session.delete()

        # no explicit return here in server v1 == 200
        return 200
