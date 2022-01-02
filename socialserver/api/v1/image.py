from socialserver.util.image import handle_upload, InvalidImageException
from socialserver.util.auth import get_user_object_from_token
from pony.orm import db_session
from flask_restful import reqparse, Resource
from json import dumps


class LegacyImageV1(Resource):

    @db_session
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("session_token", type=str, required=True)
        parser.add_argument("image_data", type=str, required=True)

        args = parser.parse_args()

        user = get_user_object_from_token(args["session_token"])
        if user is None:
            return {}, 401

        image_package = {
            "original": args['image_data']
        }

        try:
            image_info = handle_upload(dumps(image_package), user.id)
        except InvalidImageException:
            return {}, 400

        return {"sum": image_info.identifier}, 201
