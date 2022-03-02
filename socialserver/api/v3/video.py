#  Copyright (c) Niall Asher 2022

from io import BytesIO
from flask.helpers import send_file
from flask_restful import reqparse, Resource
from flask import request
from os import path
from socialserver.constants import ErrorCodes, MAX_VIDEO_SIZE_MB, VIDEO_SUPPORTED_FORMATS
from socialserver.util.file import mb_to_b, max_req_size
from pony.orm import db_session
from socialserver.util.auth import get_user_from_auth_header, auth_reqd


class Video(Resource):
    pass


class VideoThumbnail(Resource):
    pass


class NewVideo(Resource):

    @max_req_size(mb_to_b(MAX_VIDEO_SIZE_MB))
    @db_session
    @auth_reqd
    def post(self):
        pass
