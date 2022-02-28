#  Copyright (c) Niall Asher 2022

from io import BytesIO
from flask.helpers import send_file
from flask import request
from os import path
from socialserver.constants import MAX_PIXEL_RATIO, ErrorCodes, ImageTypes
from math import ceil
from socialserver.db import db
from socialserver.util.config import config
from socialserver.util.image import handle_upload, InvalidImageException
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from flask_restful import Resource, reqparse
from pony.orm import db_session

IMAGE_DIR = config.media.images.storage_dir


class Image(Resource):

    # kwargs.imageid contains the image identifier
    @db_session
    def get(self, **kwargs):

        parser = reqparse.RequestParser()
        # check out the imagetypes enum for the valid ones
        parser.add_argument('wanted_type', type=str, required=True)
        # this is a float since we want it to actually pass this parse
        # check, so we can round it after!
        parser.add_argument('pixel_ratio', type=float, required=True)
        args = parser.parse_args()

        image = db.Image.get(identifier=kwargs.get('imageid'))
        if image is None:
            return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404

        try:
            wanted_image_type = ImageTypes(args['wanted_type'])
        except ValueError:
            return {"error": ErrorCodes.IMAGE_TYPE_INVALID.value}, 400

        pixel_ratio = int(ceil(args['pixel_ratio']))
        if pixel_ratio < 1:
            pixel_ratio = 1
        if pixel_ratio > MAX_PIXEL_RATIO:
            pixel_ratio = MAX_PIXEL_RATIO

        if args['wanted_type'] == 'post':
            pixel_ratio = 1

        file = f"{IMAGE_DIR}/{kwargs.get('imageid')}/{wanted_image_type.value}_{pixel_ratio}x.jpg"

        if not path.exists(file):
            return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404

        return send_file(file)


class NewImage(Resource):

    @db_session
    @auth_reqd
    def post(self):
        if request.files.get("image") is None:
            return {"error": ErrorCodes.INVALID_IMAGE_PACKAGE.value}, 400

        image: bytes = request.files.get("image").read()

        if type(image) is not bytes:
            return {"error": ErrorCodes.INVALID_IMAGE_PACKAGE.value}, 400

        try:
            image_info = handle_upload(BytesIO(image), get_user_from_auth_header().id)
        except InvalidImageException:
            return {"error": ErrorCodes.INVALID_IMAGE_PACKAGE.value}, 400

        return {"identifier": image_info.identifier}, 201
