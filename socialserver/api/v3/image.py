#  Copyright (c) Niall Asher 2022

from io import BytesIO
from flask.helpers import send_file
from flask import request
from socialserver.constants import MAX_PIXEL_RATIO, ErrorCodes, ImageTypes, \
    ServerSupportedImageFormats, SERVER_SUPPORTED_IMAGE_FORMATS_MIMETYPES
from math import ceil
from socialserver.db import db
from socialserver.util.api.v3.error_format import format_error_return_v3
from socialserver.util.config import config
from socialserver.util.image import handle_upload, InvalidImageException
from socialserver.util.auth import auth_reqd, get_user_from_auth_header
from socialserver.util.file import max_req_size, mb_to_b, b_to_mb
from socialserver.util.output import console
from socialserver.util.filesystem import fs_images

from flask_restful import Resource, reqparse
from pony.orm import db_session

IMAGE_DIR = config.media.images.storage_dir
IMAGE_MAX_REQ_SIZE_MB = config.media.images.max_image_request_size_mb
IMAGE_MAX_REQ_SIZE = mb_to_b(IMAGE_MAX_REQ_SIZE_MB)


class Image(Resource):
    def __init__(self):
        self.get_parser = reqparse.RequestParser()
        # check out the imagetypes enum for the valid ones
        self.get_parser.add_argument("wanted_type", type=str, required=True)
        # this is a float since we want it to actually pass this parse
        # check, so we can round it after!
        self.get_parser.add_argument("pixel_ratio", type=float, required=True)
        self.get_parser.add_argument("download", type=bool, required=False)
        self.get_parser.add_argument("format", type=str, required=False)

    # kwargs.imageid contains the image identifier
    @db_session
    def get(self, **kwargs):
        args = self.get_parser.parse_args()

        # default to jpg if no or invalid format specified; it's the most compatible.
        try:
            wanted_image_format = ServerSupportedImageFormats(args.format)
        except ValueError:
            wanted_image_format = ServerSupportedImageFormats.JPG

        image = db.Image.get(identifier=kwargs.get("imageid"))
        if image is None:
            return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)

        if image.processed is False:
            return format_error_return_v3(ErrorCodes.IMAGE_NOT_PROCESSED, 404)

        try:
            wanted_image_type = ImageTypes(args.wanted_type)
        except ValueError:
            return format_error_return_v3(ErrorCodes.IMAGE_TYPE_INVALID, 400)

        pixel_ratio = int(ceil(args.pixel_ratio))
        if pixel_ratio < 1:
            pixel_ratio = 1
        if pixel_ratio > MAX_PIXEL_RATIO:
            pixel_ratio = MAX_PIXEL_RATIO

        if args.wanted_type == "post":
            pixel_ratio = 1

        file = f"/{image.sha256sum}/{wanted_image_type.value}_{pixel_ratio}x."

        # attempt to fall back to jpeg
        if not fs_images.exists(file + wanted_image_format.value):
            if wanted_image_format == ServerSupportedImageFormats.WEBP and \
                    config.media.images.jpg_fallback_when_webp_not_found:
                console.log(f"[red]Couldn't find a WEBP version of image {image.id}[/red] Attempting JPG fallback.")
                if not fs_images.exists(file + ServerSupportedImageFormats.JPG.value):
                    return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)
                wanted_image_format = ServerSupportedImageFormats.JPG
            else:
                return format_error_return_v3(ErrorCodes.IMAGE_NOT_FOUND, 404)

        file_object = fs_images.open(file + wanted_image_format.value, "rb")

        download_name = f"{image.sha256sum}.{wanted_image_format.value}"

        return send_file(
            file_object, mimetype=SERVER_SUPPORTED_IMAGE_FORMATS_MIMETYPES.get(wanted_image_format.value),
            download_name=download_name,
            as_attachment=args.download is True
        )


class NewImage(Resource):
    @max_req_size(IMAGE_MAX_REQ_SIZE)
    @db_session
    @auth_reqd
    def post(self):
        if request.files.get("image") is None:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        console.log("Files package parsed OK!")

        image: bytes = request.files.get("image").read()

        # I think we still need this, since content length can be spoofed?
        image_size_mb = b_to_mb(len(image))
        if image_size_mb > IMAGE_MAX_REQ_SIZE_MB:
            return format_error_return_v3(ErrorCodes.REQUEST_TOO_LARGE, 413)

        if type(image) is not bytes:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        try:
            image_info = handle_upload(
                BytesIO(image), get_user_from_auth_header().id, threaded=True
            )
        except InvalidImageException:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        return {
                   "identifier": image_info.identifier,
                   "processed": image_info.processed,
               }, 201


class NewImageProcessBeforeReturn(Resource):
    @max_req_size(IMAGE_MAX_REQ_SIZE)
    @db_session
    @auth_reqd
    def post(self):
        if request.files.get("image") is None:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        image: bytes = request.files.get("image").read()

        # I think we still need this, since content length can be spoofed?
        image_size_mb = b_to_mb(len(image))
        if image_size_mb > IMAGE_MAX_REQ_SIZE_MB:
            return format_error_return_v3(ErrorCodes.REQUEST_TOO_LARGE, 413)

        if type(image) is not bytes:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        try:
            image_info = handle_upload(
                BytesIO(image), get_user_from_auth_header().id, threaded=False
            )
        except InvalidImageException:
            return format_error_return_v3(ErrorCodes.INVALID_IMAGE_PACKAGE, 400)

        return {
                   "identifier": image_info.identifier,
                   "processed": image_info.processed,
               }, 201
