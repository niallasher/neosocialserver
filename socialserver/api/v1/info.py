from flask_restful import Resource
from socialserver.constants import SERVER_VERSION


class LegacyInfo(Resource):

    def get(self):
        return {
                   "inviteOnly": False,
                   "instanceName": "Socialserver",
                   "instanceVersion": SERVER_VERSION,
                   "userCanInvite": True
               }, 201
