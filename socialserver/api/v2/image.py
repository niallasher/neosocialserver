from flask.helpers import send_file
from os import path
from socialserver.constants import MAX_PIXEL_RATIO, ErrorCodes, ImageTypes
from socialserver.db import DbImage
from socialserver.util.oldconfig import config
from flask_restful import Resource, reqparse
from pony.orm import db_session


class Image(Resource):

    # kwargs.imageid contains the image identifier
    @db_session
    def get(self, **kwargs):

        parser = reqparse.RequestParser()
        # check out the imagetypes enum for the valid ones
        parser.add_argument('wanted_type', type=str, required=True)
        parser.add_argument('pixel_ratio', type=int, required=True)
        args = parser.parse_args()

        image = DbImage.get(identifier=kwargs.get('imageid'))
        if image is None:
            return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404

        try:
            wanted_image_type = ImageTypes(args['wanted_type'])
        except ValueError:
            return {"error": ErrorCodes.IMAGE_TYPE_INVALID.value}, 400

        pixel_ratio = args['pixel_ratio']
        if pixel_ratio < 1:
            pixel_ratio = 1
        if pixel_ratio > MAX_PIXEL_RATIO:
            pixel_ratio = MAX_PIXEL_RATIO

        if args['wanted_type'] == 'post':
            pixel_ratio = 1

        file = f"{config.media.images.storage_dir}/{kwargs.get('imageid')}/{wanted_image_type.value}_{pixel_ratio}x.jpg"

        if not path.exists(file):
            return {"error": ErrorCodes.IMAGE_NOT_FOUND.value}, 404

        return send_file(file)
