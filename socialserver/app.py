from flask import Flask
from flask.templating import render_template
from flask_restful import Api
from flask_cors import CORS
# this should be the first socialserver import here.
# it sets up traceback pretty printing when it's imported!
from socialserver.util.output import console
from socialserver.util.config import config
# API Version 3
from socialserver.api.v3.report import Report
from socialserver.api.v3.info import ServerInfo
from socialserver.api.v3.user_session import UserSession, UserSessionList
from socialserver.api.v3.user import User, UserInfo
from socialserver.api.v3.username_available import UsernameAvailable
from socialserver.api.v3.feed import PostFeed
from socialserver.api.v3.post import Post
from socialserver.api.v3.image import Image, NewImage
from socialserver.api.v3.block import Block
from socialserver.api.v3.follow import Follow
# API Version 1
from socialserver.api.v1.user import LegacyUser
from socialserver.api.v1.usermod import LegacyUsermod
from socialserver.api.v1.post import LegacyPost
from socialserver.api.v1.authentication import LegacyAuthentication
from socialserver.api.v1.info import LegacyInfo
from socialserver.api.v1.comment.filter_by_post import LegacyCommentFilterByPost
from socialserver.api.v1.image import LegacyImageV1
from socialserver.api.v1.post_filter.filter_by_user import LegacyPostFilterByUser


def create_app():
    application = Flask(__name__)
    CORS(application)
    api = Api(application)

    if config.misc.enable_landing_page:
        @application.get('/')
        def landing_page():
            return render_template('server_landing.html')

    api.add_resource(ServerInfo, '/api/v3/server/info')

    api.add_resource(User, '/api/v3/user')
    api.add_resource(UserInfo, '/api/v3/user/info')
    api.add_resource(UserSession, '/api/v3/user/session')
    api.add_resource(UserSessionList, '/api/v3/user/session/list')
    api.add_resource(UsernameAvailable, '/api/v3/user/name_available')

    api.add_resource(Post, '/api/v3/post/single')
    api.add_resource(PostFeed, '/api/v3/feed/posts')

    api.add_resource(Image, '/api/v3/image/<imageid>')
    api.add_resource(NewImage, '/api/v3/image')

    api.add_resource(Follow, '/api/v3/follow/user')
    api.add_resource(Block, '/api/v3/block/user')

    api.add_resource(Report, '/api/v3/report/post')

    if config.legacy.api_v1_interface.enable:
        api.add_resource(LegacyPostFilterByUser, '/api/v/1/posts/byUser')
        api.add_resource(LegacyPost, '/api/v1/posts')
        api.add_resource(LegacyCommentFilterByPost, '/api/v1/comments/byPost')
        api.add_resource(LegacyUser, '/api/v1/users')
        api.add_resource(LegacyInfo, '/api/v1/info')
        api.add_resource(LegacyUsermod, '/api/v1/usermod')
        api.add_resource(LegacyAuthentication, "/api/v1/auth")
        api.add_resource(LegacyImageV1, "/api/v1/images")

    return application
