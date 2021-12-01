from flask import Flask, request
from flask.helpers import make_response
from flask.templating import render_template
from flask_restful import Resource, Api
from werkzeug.utils import redirect
from socialserver.util.config import config
# api resources
from socialserver.api.usersession import UserSession

application = Flask(__name__)
api = Api(application)


@application.get('/')
def landing_page():
    return render_template('server_landing.html')


api.add_resource(UserSession, '/api/v2/user/session')
