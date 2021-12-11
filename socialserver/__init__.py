from flask import Flask, request
from flask.helpers import make_response
from flask.templating import render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.utils import redirect
from socialserver.util.config import config
# api stuff
from socialserver.api.usersession import UserSession, UserSessionList
from socialserver.api.user import User, UserInfo
from socialserver.api.feed import PostFeed
from socialserver.api.post import Post

application = Flask(__name__)
CORS(application)
api = Api(application)


@application.get('/')
def landing_page():
    return render_template('server_landing.html')


api.add_resource(User, '/api/v2/user')
api.add_resource(UserInfo, '/api/v2/user/info')
api.add_resource(UserSession, '/api/v2/user/session')
api.add_resource(UserSessionList, '/api/v2/user/session/list')

api.add_resource(Post, '/api/v2/post/single')
api.add_resource(PostFeed, '/api/v2/feed/posts')
