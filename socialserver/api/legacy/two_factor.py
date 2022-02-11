#  Copyright (c) Niall Asher 2022

from socialserver.util.auth import verify_password_valid, get_user_object_from_token_or_abort, \
    generate_totp_secret
import pyotp
from socialserver.util.config import config
from flask_restful import Resource, reqparse
from socialserver.constants import LegacyErrorCodes
from pony.orm import commit, db_session
from socialserver.db import db
from datetime import datetime, timedelta


class LegacyTwoFactor(Resource):

    @db_session
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])
        return {"enabled": user.totp is not None and user.totp.confirmed}, 201

    @db_session
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("session_token", type=str, required=True, help="Authentication Token")
        parser.add_argument("action", type=str, required=True, help="Action to take (add/remove/confirm)")
        # needed for removal and addition, but not confirmations
        parser.add_argument("password", type=str, required=False, help="Authentication Password")
        parser.add_argument("totp", type=str, help="Code for confirmations")

        args = parser.parse_args()

        user = get_user_object_from_token_or_abort(args['session_token'])

        # input validation, old server style
        action = args['action'].lower().strip()

        if action == 'add':

            if user.totp is not None and user.totp.confirmed is True:
                return {"err": LegacyErrorCodes.TOTP_ALREADY_ADDED.value}, 400

        elif action == 'remove':

            if user.totp is None:
                return {"err": LegacyErrorCodes.TOTP_NON_EXISTENT_CANNOT_CONFIRM.value}, 400

        elif action == 'confirm':

            if user.totp is None:
                return {"err": LegacyErrorCodes.TOTP_NON_EXISTENT_CANNOT_CONFIRM.value}, 400

        else:

            return {"err": LegacyErrorCodes.INVALID_ACTION_FIELD_ON_TOTP_POST_CALL.value}, 400

        # we need to check the password on every action except confirm
        if action != "confirm":
            if not verify_password_valid(args['password'],
                                         user.password_salt,
                                         user.password_hash):
                # this is incorrect, because the original server implementation was incorrect too.
                # fun.
                return {"err": LegacyErrorCodes.PASSWORD_DAMAGED}, 400

        # actual action logic
        if action == 'add':
            # we don't enable totp on the account,
            # since the user hasn't confirmed it yet,
            # we just create the entry and associate it
            # with the account.
            secret = generate_totp_secret()
            totp = db.Totp(
                secret=secret,
                confirmed=False,
                creation_time=datetime.utcnow()
            )
            commit()
            user.totp = totp
            # create a url to add to the authenticator
            url = pyotp.TOTP(secret).provisioning_uri(
                name=user.username,
                issuer_name=config.auth.totp.issuer)
            return {
                       "url": url
                   }, 201

        if action == 'remove':
            if user.totp is not None:
                totp = user.totp
                user.totp = None
                totp.delete()
                return {}, 201
            return {}, 400

        if action == "confirm":
            # fail out if the user doesn't have a totp, or already has an active one
            if user.totp is None or user.totp.confirmed is True:
                return {"err": LegacyErrorCodes.TOTP_INCORRECT.value}, 401
            # in this case, the TOTP has expired. Legacy client only handles TOTP_INCORRECT here, so that's what
            # we have to send back to fail somewhat gracefully.
            if datetime.utcnow() > user.totp.creation_time + timedelta(
                    seconds=config.auth.totp.unconfirmed_expiry_time):
                return {"err": LegacyErrorCodes.TOTP_INCORRECT.value}, 401
            auth = pyotp.TOTP(user.totp.secret)
            if auth.verify(args['totp']):
                user.totp.confirmed = True
                return {}, 201
            return {"err": LegacyErrorCodes.TOTP_INCORRECT.value}, 401

        return {"err": LegacyErrorCodes.GENERIC_SERVER_ERROR.value}, 500
