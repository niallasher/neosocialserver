from flask_restful import Resource
from socialserver.constants import SERVER_VERSION
from socialserver.util.auth import auth_reqd


class ServerInfo(Resource):

    # flask-restful doesn't seem to work with static methods.
    # this method is no exception. if you make it static,
    # it won't work.

    # noinspection PyMethodMayBeStatic
    def get(self):
        return {
                   "version": SERVER_VERSION,
               }, 201
