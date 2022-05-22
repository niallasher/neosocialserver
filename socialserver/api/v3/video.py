#  Copyright (c) Niall Asher 2022

from io import BytesIO
from flask.helpers import send_file
from flask_restful import Resource, reqparse
from flask import request
from socialserver.constants import ErrorCodes, MAX_VIDEO_SIZE_MB
from socialserver.util.file import mb_to_b, max_req_size, b_to_mb
from pony.orm import db_session
from socialserver.util.auth import get_user_from_auth_header, auth_reqd
from socialserver.util.video import handle_video_upload, InvalidVideoException
from socialserver.db import db
from socialserver.util.filesystem import fs_videos


class Video(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        self.get_parser.add_argument("download", type=bool, required=False)

    @db_session
    def get(self, **kwargs):

        args = self.get_parser.parse_args()

        video = db.Video.get(identifier=kwargs.get("videoid"))
        if video is None:
            return {"error": ErrorCodes.OBJECT_NOT_FOUND.value}, 404

        file = f"/{video.sha256sum}/video.mp4"
        if not fs_videos.exists(file):
            return {"error": ErrorCodes.OBJECT_NOT_FOUND.value}, 404

        # doesn't seem very efficient.
        file_buffer = BytesIO(fs_videos.readbytes(file))

        print(args)

        download_name = f"{video.sha256sum}.mp4"
        if args["download"] is True:
            print("Abc")

        file_object = fs_videos.open(file, "rb")

        return send_file(
            file_buffer,
            download_name=download_name,
            as_attachment=args["download"] is True,
        )


class NewVideo(Resource):
    @max_req_size(mb_to_b(MAX_VIDEO_SIZE_MB))
    @db_session
    @auth_reqd
    def post(self):

        user = get_user_from_auth_header()

        if request.files.get("video") is None:
            return {"error": ErrorCodes.INVALID_VIDEO.value}, 400

        video: bytes = request.files.get("video").read()

        video_size_mb = b_to_mb(len(video))
        if video_size_mb > MAX_VIDEO_SIZE_MB:
            return {"error": ErrorCodes.REQUEST_TOO_LARGE.value}, 413

        if type(video) is not bytes:
            return {"error": ErrorCodes.INVALID_VIDEO.value}, 400

        try:
            video_info = handle_video_upload(BytesIO(video), user.id)
        except InvalidVideoException:

            return {"error": ErrorCodes.INVALID_VIDEO.value}, 400

        return {"identifier": video_info.identifier}, 201
