from flask_restful import Resource
from socialserver.constants import SERVER_VERSION
from socialserver.util.config import config


class ServerInfo(Resource):

    # flask-restful doesn't seem to work with static methods.
    # this method is no exception. if you make it static,
    # it won't work.

    # noinspection PyMethodMayBeStatic
    def get(self):
        return {
                   "version": SERVER_VERSION,
                   "approval_required": config.auth.registration.approval_required,
               }, 201
