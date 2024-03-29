#  Copyright (c) Niall Asher 2022

from flask import Flask
from flask.templating import render_template
from flask_restful import Api
from flask_cors import CORS

# this should be the first socialserver import here.
# it sets up traceback pretty printing when it's imported!
from socialserver.util.output import console
from socialserver.api.v3.bookmark import BookmarkPost, BookmarkFeed
from socialserver.api.v3.follow_list import FollowerList, FollowingList
from socialserver.api.v3.post_like_list import PostLikeList
from socialserver.util.config import config
from socialserver.maintenance import maintenance
from socialserver.util.post import start_unprocessed_post_thread

# API Version 3
from socialserver.api.v3.comment import Comment
from socialserver.api.v3.report import Report
from socialserver.api.v3.info import ServerInfo
from socialserver.api.v3.user_session import UserSession, UserSessionList
from socialserver.api.v3.user import User, UserInfo
from socialserver.api.v3.username_available import UsernameAvailable
from socialserver.api.v3.feed import PostFeed
from socialserver.api.v3.post import Post
from socialserver.api.v3.post_like import PostLike
from socialserver.api.v3.image import Image, NewImage, NewImageProcessBeforeReturn
from socialserver.api.v3.block import Block
from socialserver.api.v3.follow import Follow
from socialserver.api.v3.two_factor import (
    TwoFactorAuthentication,
    TwoFactorAuthenticationVerification,
)
from socialserver.api.v3.user_password_change import UserPasswordChange
from socialserver.api.v3.comment_feed import CommentFeed
from socialserver.api.v3.comment_like import CommentLike
from socialserver.api.v3.video import NewVideo, Video

# API Version 3 Admin stuff
from socialserver.api.v3.admin.user_approvals import UserApprovals

# API legacy (v1/v2, it's confusing!)
from socialserver.api.legacy.like import LegacyLike
from socialserver.api.legacy.bio import LegacyUserBio
from socialserver.api.legacy.follows import LegacyUserFollows, LegacyUserFollowing
from socialserver.api.legacy.user import LegacyUser
from socialserver.api.legacy.usermod import LegacyUsermod
from socialserver.api.legacy.post import LegacyPost
from socialserver.api.legacy.authentication import LegacyAuthentication
from socialserver.api.legacy.info import LegacyInfo
from socialserver.api.legacy.comment_filter.filter_by_post import (
    LegacyCommentFilterByPost,
)
from socialserver.api.legacy.image import LegacyImage
from socialserver.api.legacy.post_filter.by_user import LegacyPostFilterByUser
from socialserver.api.legacy.like_filter.by_post import LegacyLikeFilterByPost
from socialserver.api.legacy.follower_list import LegacyFollower
from socialserver.api.legacy.block import LegacyBlock, LegacyUserBlocks
from socialserver.api.legacy.comment import LegacyComment
from socialserver.api.legacy.comment import LegacyCommentLike
from socialserver.api.legacy.user_deauth import LegacyAllDeauth
from socialserver.api.legacy.invite_codes import LegacyInviteCodes
from socialserver.api.legacy.privileged_ops.admin_usermod import LegacyAdminUserMod
from socialserver.api.legacy.privileged_ops.admin_delete_user import (
    LegacyAdminDeleteUser,
)
from socialserver.api.legacy.privileged_ops.admin_delete_post import (
    LegacyAdminDeletePost,
)
from socialserver.api.legacy.modqueue import LegacyModQueue
from socialserver.api.legacy.two_factor import LegacyTwoFactor

TOTP_REPLAY_PREVENTION_ENABLED = config.auth.totp.replay_prevention_enabled
LESS_SECURE_PASSWORD_CHANGE_ENABLED = (
    config.legacy_api_interface.enable_less_secure_password_change
)
LEGACY_INTERFACE_ENABLED = config.legacy_api_interface.enable
FAILURE_LOCK_ENABLED = config.auth.failure_lock.enabled


def create_app():
    application = Flask(__name__)
    CORS(application)
    api = Api(application)

    # stuff that gets setup before the server processes
    # its first request.
    @application.before_first_request
    def _setup():
        start_unprocessed_post_thread()

    if not TOTP_REPLAY_PREVENTION_ENABLED:
        console.log("[bold red]TOTP replay prevention is disabled!")

    if not FAILURE_LOCK_ENABLED:
        console.log("[bold red]auth.failure_lock is disabled! This is not recommended for production deployments!")

    if config.misc.enable_landing_page:
        @application.get("/")
        def landing_page():
            return render_template(
                "server_landing.html", legacy_interface_enabled=LEGACY_INTERFACE_ENABLED
            )

    api.add_resource(ServerInfo, "/api/v3/server/info")

    api.add_resource(UsernameAvailable, "/api/v3/username/available")

    api.add_resource(User, "/api/v3/user")
    api.add_resource(UserPasswordChange, "/api/v3/user/password")
    api.add_resource(UserInfo, "/api/v3/user/info")
    api.add_resource(UserSession, "/api/v3/user/session")
    api.add_resource(UserSessionList, "/api/v3/user/session/list")
    api.add_resource(TwoFactorAuthentication, "/api/v3/user/2fa")
    api.add_resource(TwoFactorAuthenticationVerification, "/api/v3/user/2fa/verify")
    api.add_resource(Follow, "/api/v3/user/follow")
    api.add_resource(Block, "/api/v3/user/block")

    api.add_resource(FollowerList, "/api/v3/user/followers")
    api.add_resource(FollowingList, "/api/v3/user/following")

    api.add_resource(Post, "/api/v3/posts/single")
    api.add_resource(PostFeed, "/api/v3/posts/feed")
    api.add_resource(Report, "/api/v3/posts/report")
    api.add_resource(PostLike, "/api/v3/posts/like")
    api.add_resource(PostLikeList, "/api/v3/posts/like/feed")

    api.add_resource(BookmarkPost, "/api/v3/posts/bookmark")
    api.add_resource(BookmarkFeed, "/api/v3/posts/bookmark/feed")

    api.add_resource(Comment, "/api/v3/comments")
    api.add_resource(CommentFeed, "/api/v3/comments/feed")
    api.add_resource(CommentLike, "/api/v3/comments/like")

    api.add_resource(Image, "/api/v3/image/<imageid>")
    api.add_resource(NewImage, "/api/v3/image")
    api.add_resource(NewImageProcessBeforeReturn, "/api/v3/image/process_before_return")

    api.add_resource(Video, "/api/v3/videos/<videoid>")
    api.add_resource(NewVideo, "/api/v3/videos")

    api.add_resource(UserApprovals, "/api/v3/admin/userApprovals")

    if config.legacy_api_interface.enable:
        console.log(
            "[bold red]Legacy interface enabled!\nThis might reduce security."
        )

        if LESS_SECURE_PASSWORD_CHANGE_ENABLED:
            console.log(
                "[bold red]Insecure password change enabled.\n"
                + "Please only enable this for compatibility reasons"
            )

        api.add_resource(LegacyPostFilterByUser, "/api/v1/posts/byUser")
        api.add_resource(LegacyPost, "/api/v1/posts")
        api.add_resource(LegacyCommentFilterByPost, "/api/v1/comments/byPost")
        api.add_resource(LegacyUser, "/api/v1/users")
        api.add_resource(LegacyInfo, "/api/v1/info")
        api.add_resource(LegacyUsermod, "/api/v1/usermod")
        api.add_resource(LegacyAuthentication, "/api/v1/auth")
        api.add_resource(LegacyImage, "/api/v1/images")
        api.add_resource(LegacyUserFollows, "/api/v1/followers/userFollows")
        api.add_resource(LegacyUserBio, "/api/v1/users/bio")
        api.add_resource(LegacyUserFollowing, "/api/v1/followers/followsUser")
        api.add_resource(LegacyLikeFilterByPost, "/api/v1/likes/byPost")
        api.add_resource(LegacyLike, "/api/v1/likes")
        api.add_resource(LegacyFollower, "/api/v1/followers")
        api.add_resource(LegacyBlock, "/api/v1/block")
        api.add_resource(LegacyUserBlocks, "/api/v1/users/blockList")
        api.add_resource(LegacyComment, "/api/v1/comments")
        api.add_resource(LegacyInviteCodes, "/api/v1/invitecodes")
        api.add_resource(LegacyAdminUserMod, "/api/v1/admin/usermod")
        api.add_resource(LegacyAdminDeleteUser, "/api/v1/admin/userdel")
        api.add_resource(LegacyAdminDeletePost, "/api/v1/admin/postdel")
        api.add_resource(LegacyModQueue, "/api/v1/modqueue")
        api.add_resource(LegacyCommentLike, "/api/v2/comments/like")
        api.add_resource(LegacyAllDeauth, "/api/v2/user/deauth")
        api.add_resource(LegacyTwoFactor, "/api/v2/user/twofactor")

    # run startup maintenance
    maintenance()

    return application
