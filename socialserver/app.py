from flask import Flask
from flask.templating import render_template
from flask_restful import Api
from flask_cors import CORS
# this should be the first socialserver import here.
# it sets up traceback pretty printing when it's imported!
from socialserver.util.output import console
from socialserver.util.config import config
# API Version 2
from socialserver.api.v2.report import Report
from socialserver.api.v2.info import ServerInfo
from socialserver.api.v2.user_session import UserSession, UserSessionList
from socialserver.api.v2.user import User, UserInfo
from socialserver.api.v2.username_available import UsernameAvailable
from socialserver.api.v2.feed import PostFeed
from socialserver.api.v2.post import Post
from socialserver.api.v2.image import Image
from socialserver.api.v2.block import Block
from socialserver.api.v2.follow import Follow


def create_app():
    application = Flask(__name__)
    CORS(application)
    api = Api(application)

    if config.misc.enable_landing_page:

        @application.get('/')
        def landing_page():
            return render_template('server_landing.html')

    api.add_resource(ServerInfo, '/api/v2/server/info')

    api.add_resource(User, '/api/v2/user')
    api.add_resource(UserInfo, '/api/v2/user/info')
    api.add_resource(UserSession, '/api/v2/user/session')
    api.add_resource(UserSessionList, '/api/v2/user/session/list')
    api.add_resource(UsernameAvailable, '/api/v2/user/name_available')

    api.add_resource(Post, '/api/v2/post/single')
    api.add_resource(PostFeed, '/api/v2/feed/posts')

    api.add_resource(Image, '/api/v2/image/<imageid>')

    api.add_resource(Follow, '/api/v2/follow/user')
    api.add_resource(Block, '/api/v2/block/user')

    api.add_resource(Report, '/api/v2/report/post')

    if config.legacy.api_v1_interface.enable:
        console.log("[red]Warning:[/red] The v1 legacy interface hasn't been implemented yet!")

    return application
