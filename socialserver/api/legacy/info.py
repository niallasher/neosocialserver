#  Copyright (c) Niall Asher 2022

from flask_restful import Resource
from socialserver.constants import SERVER_VERSION
from socialserver.util.config import config

# this probably needs a better name, but i can't think of one right now...
SHOULD_RETURN_LEGACY_VERSION_STRING = config.legacy_api_interface.report_legacy_version


class LegacyInfo(Resource):

    # noinspection PyMethodMayBeStatic
    def get(self):
        return {
                   "inviteOnly": False,
                   "instanceName": "Socialserver",
                   "instanceVersion": "2.99.0"
                   if SHOULD_RETURN_LEGACY_VERSION_STRING
                   else SERVER_VERSION,
                   "userCanInvite": True,
               }, 201
