#  Copyright (c) Niall Asher 2022
from socialserver.util.image import (
    handle_upload,
    InvalidImageException,
    convert_data_url_to_byte_buffer,
)
from socialserver.util.file import max_req_size, mb_to_b, b_to_mb
from socialserver.util.auth import get_user_object_from_token_or_abort
from socialserver.util.config import config
from pony.orm import db_session
from flask_restful import reqparse, Resource

IMAGE_MAX_REQ_SIZE_MB = config.media.images.max_image_request_size_mb
IMAGE_MAX_REQ_SIZE = mb_to_b(IMAGE_MAX_REQ_SIZE_MB)


class LegacyImage(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("session_token", type=str, required=True)
        self.post_parser.add_argument("image_data", type=str, required=True)

    @max_req_size(IMAGE_MAX_REQ_SIZE)
    @db_session
    def post(self):
        args = self.post_parser.parse_args()

        image = convert_data_url_to_byte_buffer(args["image_data"])
        if b_to_mb(len(image.read())) > IMAGE_MAX_REQ_SIZE:
            # nothing else we can return to the legacy server!
            return {}, 400
        # return pointer to the start so we can read again later.
        image.seek(0)

        user = get_user_object_from_token_or_abort(args["session_token"])

        try:
            # legacy doesn't have any ux to handle unprocessed posts/images,
            # so we're not going to enable threading for now.
            # TODO: maybe this should be a configurable?
            image_info = handle_upload(image, user.id, threaded=False)
        except InvalidImageException:
            return {}, 400

        return {"sum": image_info.identifier}, 201
