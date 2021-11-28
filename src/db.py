from enum import unique
from pony import orm
import datetime
from constants import BIO_MAX_LEN, COMMENT_MAX_LEN, DISPLAY_NAME_MAX_LEN, REPORT_SUPPLEMENTARY_INFO_MAX_LEN, TAG_MAX_LEN, USERNAME_MAX_LEN, AccountAttributes
from pony.orm import ormtypes
from configutil import config


db = orm.Database()


class DbUser(db.Entity):
    sessions = orm.Set("DbUserSession")
    display_name = orm.Required(str, max_len=DISPLAY_NAME_MAX_LEN)
    username = orm.Required(str, max_len=USERNAME_MAX_LEN, unique=True)
    password_hash = orm.Required(str)
    password_salt = orm.Required(str)
    creation_time = orm.Required(datetime.datetime)
    # check out AccountAttributes enum in constants for more info
    account_attributes = orm.Required(orm.IntArray)
    bio = orm.Required(str, nullable=True, max_len=BIO_MAX_LEN)
    totp_secret = orm.Optional(str, nullable=True)
    last_used_totp = orm.Optional(str, nullable=True)
    posts = orm.Set('DbPost', cascade_delete=True)
    comments = orm.Set('DbComment', cascade_delete=True)
    post_likes = orm.Set('DbPostLike', cascade_delete=True)
    comment_likes = orm.Set('DbCommentLike', cascade_delete=True)
    followers = orm.Set("DbFollow", cascade_delete=True)
    following = orm.Set("DbFollow", cascade_delete=True)
    blocked_users = orm.Set("DbBlock", cascade_delete=True)
    blocked_by = orm.Set("DbBlock", cascade_delete=True)
    invite_codes = orm.Set("DbInviteCode", cascade_delete=True)
    profile_pic = orm.Optional("DbImage")
    header_pic = orm.Optional("DbImage")
    uploaded_images = orm.Set("DbImage", reverse="uploader")
    # deleting user should leave reports intact
    submitted_reports = orm.Set("DbPostReport", cascade_delete=False)

    @property
    def is_private(self):
        return AccountAttributes.PRIVATE.value in self.account_attributes

    @property
    def is_verified(self):
        return AccountAttributes.VERIFIED.value in self.account_attributes

    @property
    def is_admin(self):
        return AccountAttributes.ADMIN.value in self.account_attributes

    @property
    def is_moderator(self):
        return AccountAttributes.MODERATOR.value in self.account_attributes

    @property
    def has_config_permissions(self):
        return AccountAttributes.INSTANCE_ADMIN.value in self.account_attributes


class DbUserSession(db.Entity):
    # here for security purposes.
    # need to make sure this collection is clear,
    # and it's made obvious to the user that its
    # not for advertising purposes.
    access_token = orm.Required(str)
    user = orm.Required('DbUser')
    creation_ip = orm.Required(str)
    creation_time = orm.Required(datetime.datetime)
    last_access_time = orm.Required(datetime.datetime)
    user_agent = orm.Required(str)


class DbPost(db.Entity):
    # whether the post is currently in the modqueue
    under_moderation = orm.Required(bool)
    user = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    text = orm.Required(str)
    images = orm.Set('DbImage', reverse="associated_posts")
    comments = orm.Set('DbComment', cascade_delete=True)
    likes = orm.Set('DbPostLike', cascade_delete=True)
    hashtags = orm.Set('DbHashtag')
    reports = orm.Set('DbPostReport', cascade_delete=True)


class DbPostReport(db.Entity):
  # we want to ensure that the report has a user,
  # but we don't want to remove it if the user
  # leaves the platform, for safety & legal reasons
    reporter = orm.Optional('DbUser', reverse="submitted_reports")
    post = orm.Required('DbPost', reverse="reports")
    creation_time = orm.Required(datetime.datetime)
    supplementary_info = orm.Optional(
        str, max_len=REPORT_SUPPLEMENTARY_INFO_MAX_LEN)


class DbImage(db.Entity):
    uploader = orm.Set('DbUser')
    hash = orm.Required(str, unique=True)
    associated_profile_pics = orm.Set('DbUser', reverse='profile_pic')
    associated_header_pics = orm.Set('DbUser', reverse='header_pic')
    associated_posts = orm.Set('DbPost', reverse='images')


class DbHashtag(db.Entity):
    creation_time = orm.Required(datetime.datetime)
    name = orm.Required(str, max_len=TAG_MAX_LEN, unique=True)
    posts = orm.Set('DbPost', reverse='hashtags')


class DbPostLike(db.Entity):
    user = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    post = orm.Required('DbPost')


class DbCommentLike(db.Entity):
    user = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    comment = orm.Required('DbComment')


class DbFollow(db.Entity):
    user = orm.Required('DbUser', reverse='following')
    following = orm.Required('DbUser', reverse='followers')
    creation_time = orm.Required(datetime.datetime)


class DbComment(db.Entity):
    user = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    text = orm.Required(str, max_len=COMMENT_MAX_LEN)
    post = orm.Required('DbPost')
    likes = orm.Set('DbCommentLike', cascade_delete=True)


class DbBlock(db.Entity):
    user = orm.Required('DbUser', reverse='blocked_users')
    blocking = orm.Required('DbUser', reverse='blocked_by')
    creation_time = orm.Required(datetime.datetime)


class DbInviteCode(db.Entity):
    user = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    code = orm.Required(str)
    used = orm.Required(bool)


def _bind_db():
    if config.database.connector == 'sqlite':
        db.bind('sqlite', config.database.address, create_db=True)
    elif config.database.connector == 'postgres':
        # TODO: add postgres support back in
        print("Sorry, postgres support has not been reintegrated yet.")
    else:
        raise ValueError("Invalid connector specified in config file.")


_bind_db()

db.generate_mapping(create_tables=True)
