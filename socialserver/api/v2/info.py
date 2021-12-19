from flask_restful import Resource, reqparse
from socialserver.constants import SERVER_VERSION
from socialserver.util.config import config


class ServerInfo(Resource):

    # Ignore the ide. This shouldn't be a static method.
    # It doesn't seem to work with flask-restful when it is.
    def get(self):

        reg_type = 0

        return {
            "version": SERVER_VERSION,
        },
