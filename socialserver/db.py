from enum import unique
from pony import orm
import datetime
from socialserver.constants import BIO_MAX_LEN, COMMENT_MAX_LEN, DISPLAY_NAME_MAX_LEN, \
    REPORT_SUPPLEMENTARY_INFO_MAX_LEN, TAG_MAX_LEN, USERNAME_MAX_LEN, AccountAttributes
from socialserver.util.config import config


db = orm.Database()


class DbUser(db.Entity):
    sessions = orm.Set("DbUserSession")
    display_name = orm.Required(str, max_len=DISPLAY_NAME_MAX_LEN)
    username = orm.Required(str, max_len=USERNAME_MAX_LEN, unique=True)
    password_hash = orm.Required(str)
    password_salt = orm.Required(str)
    creation_time = orm.Required(datetime.datetime)
    birthday = orm.Optional(datetime.date)
    # legacy accounts are the ones imported from socialserver 2.x during migration
    # this doesn't mean much now, but might becomne important in the future
    # so might as well have it.
    is_legacy_account = orm.Required(bool)
    # check out AccountAttributes enum in constants for more info
    account_attributes = orm.Required(orm.IntArray)
    bio = orm.Optional(str, max_len=BIO_MAX_LEN)
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
    associated_api_keys = orm.Set("DbApiKey", cascade_delete=True)
    # whether the account is approved. this will be made true
    # automatically if admin approval requirement is off.
    account_approved = orm.Required(bool)

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

    @property
    def has_profile_picture(self):
        return self.profile_pic is not None

    @property
    def has_header_picture(self):
        return self.header_pic is not None


class DbUserSession(db.Entity):
    # data collection is for security purposes.
    # need to note that it's not used for advertising.
    # we hash the access token unsalted & hashed with sha256,
    # same as an API key.
    # check DbApiKey for a quick explanation of why.
    access_token_hash = orm.Required(str)
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
    # we don't want to just delete these I don't think?
    # better to mark them inactive, until the post is deleted.
    # that way if it's moderated, an admin can still see the acted
    # on report. rather than expose deletion via the API, we should
    # just rely on database constraints to delete reports when the
    # post they are associated with has been removed.
    # IMPORTANT NOTE: could this result in users posting illegal things
    # and then deleting them soon after to prevent reports being seen by a
    # moderator? this needs investigating, but i can't think of a clean
    # solution right now.
    active = orm.Required(bool)
    # we want to ensure that the report has a user,
    # but we don't want to actually tie it to a user,
    # since if somebody reports illegal content, and then
    # deletes their account, we still want to know about
    # the report so we can take action
    reporter = orm.Optional('DbUser', reverse="submitted_reports")
    post = orm.Required('DbPost', reverse="reports")
    creation_time = orm.Required(datetime.datetime)
    # since we do one report per post, we want to be able to
    # report multiple infringements at once, hence the array.
    # NOTE: not sure we do want this? Need to figure that one
    # out soon I guess.
    # check out the socialserver.constants.ReportReasons enum
    # for a list of these.
    report_reason = orm.Required(orm.IntArray)
    supplementary_info = orm.Optional(
        str, max_len=REPORT_SUPPLEMENTARY_INFO_MAX_LEN)


class DbImage(db.Entity):
    uploader = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    # uuid used to retrieve the image from storage
    identifier = orm.Required(str)
    # upload_hash = orm.Required(str)
    associated_profile_pics = orm.Set('DbUser', reverse='profile_pic')
    associated_header_pics = orm.Set('DbUser', reverse='header_pic')
    associated_posts = orm.Set('DbPost', reverse='images')
    # SHA256 hash of the original file, for later adaption
    # original_hash = orm.Required(str)

    @property
    def is_orphan(self):
        return len(self.associated_posts) == 0 and len(self.associated_profile_pics) == 0 \
               and len(self.associated_header_pics) == 0


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


class DbApiKey(db.Entity):
    owner = orm.Required('DbUser')
    creation_time = orm.Required(datetime.datetime)
    # we store this with sha256, not pbkdf2 or argon2,
    # since we want it to be super fast, as each request
    # will have to verify it if it's in use.
    # no point salting it since it's high entropy already,
    # and practically impossible to build a lookup table for
    key_hash = orm.Required(str)
    permissions = orm.Required(orm.IntArray)  # constants.ApiKeyPermissions


def _bind_db():
    if config.database.connector == 'sqlite':
        db.bind('sqlite', config.database.address, create_db=True)
    elif config.database.connector == 'postgres':
        # TODO: add postgres support back in
        db.bind('postgres', config.database.address)
    else:
        raise ValueError("Invalid connector specified in config file.")


_bind_db()

db.generate_mapping(create_tables=True)
