from flask_restful import Resource, reqparse
from socialserver.constants import SERVER_VERSION
from socialserver.util.config import config


def ServerInfo(Resource):

    def get(self):

        reg_type = 0

        return {
            "version": SERVER_VERSION,
        },
