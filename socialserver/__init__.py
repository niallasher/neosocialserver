from flask import Flask, request
from flask.helpers import make_response
from flask.templating import render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.utils import redirect
from socialserver.api.v2.report import Report
from socialserver.util.config import config
# API
# Version 2 (current as of 3.x) (note: should this be renamed to apiv3?)
# Just for major server version parity? The official client is going to use
# a sync-ed major version to denote basic compatibility, followed by minor
# for QoL upgrades most likely, so maybe the api should?
from socialserver.api.v2.usersession import UserSession, UserSessionList
from socialserver.api.v2.user import User, UserInfo
from socialserver.api.v2.feed import PostFeed
from socialserver.api.v2.post import Post
from socialserver.api.v2.image import Image
from socialserver.api.v2.block import Block
from socialserver.api.v2.follow import Follow

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

api.add_resource(Image, '/api/v2/image/<imageid>')

api.add_resource(Follow, '/api/v2/follow/user')
api.add_resource(Block, '/api/v2/block/user')

api.add_resource(Report, '/api/v2/report/post')

if config.legacy.api_v1_compat.enable:
    print("Legacy API has not been implemented yet.")
