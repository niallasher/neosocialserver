from datetime import datetime
from socialserver.db import db, DbUser, DbUserSession
from flask_restful import Resource, Api, reqparse
from pony.orm import db_session
from flask import request
from socialserver.constants import ErrorCodes
from socialserver.util.auth import generate_key, get_ip_from_request, get_username_from_token, hash_plaintext_sha256, verify_password_valid


class UserSession(Resource):

    @db_session
    def get(self):

        # TODO: some sort of generic token check instead
        # of having to write this each time
        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        args = parser.parse_args()

        session = DbUserSession.get(
            access_token_hash=hash_plaintext_sha256(args['access_token']))

        if session is None:
            return {'error': ErrorCodes.TOKEN_INVALID.value}, 401

        return ({
            "owner": session.user.username,
            "current_ip": get_ip_from_request(request),
            "creation_ip": session.creation_ip,
            "creation_time": session.creation_time.timestamp(),
            "current_server_time": datetime.now().timestamp(),
            "last_access_time": session.last_access_time.timestamp(),
            "user_agent": session.user_agent
        },
            200)

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

    @db_session
    def delete(self):

        parser = reqparse.RequestParser()
        parser.add_argument('access_token', type=str, required=True)
        args = parser.parse_args()

        session = DbUserSession.get(
            access_token_hash=hash_plaintext_sha256(args['access_token']))
        if session == None:
            return {'error': ErrorCodes.TOKEN_INVALID.value}, 401

        session.delete()
        return {}, 201
