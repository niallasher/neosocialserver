from flask import Flask, request
from flask.helpers import make_response
from flask.templating import render_template
from flask_restful import Resource, Api
from werkzeug.utils import redirect
from socialserver.util.config import config
# api resources
from socialserver.api.usersession import UserSession, UserSessionList
from socialserver.api.user import UserInfo

application = Flask(__name__)
api = Api(application)


@application.get('/')
def landing_page():
    return render_template('server_landing.html')


api.add_resource(UserInfo, '/api/v2/user/info')
api.add_resource(UserSession, '/api/v2/user/session')
api.add_resource(UserSessionList, '/api/v2/user/session/list')
