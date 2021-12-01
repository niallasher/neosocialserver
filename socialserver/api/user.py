from datetime import datetime
from socialserver.db import db, DbUser, DbUserSession
from flask_restful import Resource, Api, reqparse
from pony.orm import db_session
from flask import request
from socialserver.constants import ErrorCodes
from socialserver.util.auth import generate_key, get_ip_from_request, verify_password_valid


class UserSession(Resource):
    def get(self):
        return {'message': "ok"}

    @db_session
    def post(self):

        # TODO: reimplement TOTP
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        user = DbUser.get(username=args['username'])
        if user is None:
            return {'error': ErrorCodes.USERNAME_NOT_FOUND.value}, 404

        if not verify_password_valid(args['password'], user.password_salt, user.password_hash):
            return {'error': ErrorCodes.INCORRECT_PASSWORD.value}, 401

        secret = generate_key()

        DbUserSession(
            user=user,
            access_token_hash=secret.hash,
            creation_ip=get_ip_from_request(request),
            creation_time=datetime.now(),
            last_access_time=datetime.now(),
            user_agent=request.headers.get('User-Agent')
        )

        return {"access_token": secret.key}, 200

    def delete(self):
        return {'message': 'Goodbye World!'}
