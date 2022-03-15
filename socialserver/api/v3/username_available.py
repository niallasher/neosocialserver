#  Copyright (c) Niall Asher 2022

from socialserver.constants import REGEX_USERNAME_VALID, ErrorCodes
from socialserver.db import db
from pony.orm import db_session
from flask_restful import Resource, reqparse
import re


class UsernameAvailable(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("username", type=str, required=True)

    @db_session
    def get(self):
        args = self.get_parser.parse_args()

        if not bool(re.match(REGEX_USERNAME_VALID, args["username"])):
            return {"error": ErrorCodes.USERNAME_INVALID.value}, 400

        existing_user = db.User.get(username=args["username"])

        return existing_user is None, 200
