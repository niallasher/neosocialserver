#  Copyright (c) Niall Asher 2022

from flask_restful import Resource, reqparse
from socialserver.db import db
from socialserver.util.auth import auth_reqd, get_user_from_auth_header, check_totp_valid, verify_password_valid, \
    generate_totp_secret, TotpInvalidException
from pony.orm import db_session, commit
from socialserver.constants import ErrorCodes
from socialserver.util.config import config
from datetime import datetime, timedelta


class TwoFactorAuthentication(Resource):

    @auth_reqd
    @db_session
    # return true if the user has 2FA, & it's confirmed
    def get(self):
        user = get_user_from_auth_header()
        return user.totp is not None and user.totp.confirmed is True

    @auth_reqd
    @db_session
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        user = get_user_from_auth_header()

        if not verify_password_valid(args['password'], user.password_salt, user.password_hash):
            return {"error": ErrorCodes.INCORRECT_PASSWORD.value}, 401

        if user.totp is None:
            return {"error": ErrorCodes.TOTP_NOT_ACTIVE.value}, 400

        totp = user.totp
        user.totp = None
        totp.delete()

        return {}, 200

    @auth_reqd
    @db_session
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("password", type=str, required=True)
        args = parser.parse_args()

        user = get_user_from_auth_header()

        if not verify_password_valid(args['password'], user.password_salt, user.password_hash):
            return {"error": ErrorCodes.INCORRECT_PASSWORD.value}, 401

        # handle existing totp. we only want to fail if it's confirmed!
        if user.totp is not None:
            if user.totp.confirmed is False:
                # remove old unconfirmed code entry if it's still attached
                # (i.e. hasn't yet been removed due to timeout)
                old_totp = user.totp
                user.totp = None
                old_totp.delete()
            elif user.totp.confirmed:
                # if the code is confirmed, it's active, and we don't want
                # to overwrite it, so we fail out with an error
                # (any client should explicitly remove it first!)
                return {"error": ErrorCodes.TOTP_ALREADY_ACTIVE.value}, 400

        secret = generate_totp_secret()
        name = user.username
        issuer = config.auth.totp.issuer

        # unconfirmed; user will have to verify before we activate it,
        # in case something goes wrong before they've added it to their
        # authenticator (e.g. closed client before adding.)
        totp = db.Totp(
            secret=secret,
            confirmed=False,
            creation_time=datetime.utcnow()
        )

        # make sure the totp is committed to the database
        # before we assign it to the user object
        commit()

        user.totp = totp

        # in v3 we don't return urls. a client create them instead.
        # we just want to return the actual info they need to do so
        # ( or present any other way of adding the info )
        return {
                   "secret": secret,
                   "name": name,
                   "issuer": issuer,
                   # not implemented yet!
                   # unconfirmed codes will be removed after this time.
                   # not great for legacy UX, but not much can be done
                   # about that
                   "time_until_expiry": config.auth.totp.unconfirmed_expiry_time
               }, 201


# it's a mouthful lol
class TwoFactorAuthenticationVerification(Resource):

    @auth_reqd
    @db_session
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("totp", type=str, required=True)
        args = parser.parse_args()

        user = get_user_from_auth_header()

        if user.totp is None:
            return {"error": ErrorCodes.TOTP_NOT_ACTIVE.value}, 400

        if user.totp is not None and user.totp.confirmed:
            return {"error": ErrorCodes.TOTP_ALREADY_ACTIVE.value}, 400

        if datetime.utcnow() > user.totp.creation_time + timedelta(seconds=config.auth.totp.unconfirmed_expiry_time):
            return {"error": ErrorCodes.TOTP_NOT_ACTIVE.value}, 400

        try:
            check_totp_valid(args['totp'], user)
        # TotpExpendedException can't be raised here (if it is,
        # the code has issues) since the code is only expended on
        # a successful check_totp_valid call, and the first time that
        # can happen is a *successful* verification!
        except TotpInvalidException:
            return {"error": ErrorCodes.TOTP_INCORRECT.value}, 400

        user.totp.confirmed = True
        return {}, 201
