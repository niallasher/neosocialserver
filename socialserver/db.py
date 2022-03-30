#  Copyright (c) Niall Asher 2022

from pony import orm
import datetime
from socialserver.constants import (
    BIO_MAX_LEN,
    COMMENT_MAX_LEN,
    DISPLAY_NAME_MAX_LEN,
    REPORT_SUPPLEMENTARY_INFO_MAX_LEN,
    TAG_MAX_LEN,
    USERNAME_MAX_LEN,
    AccountAttributes,
)
from socialserver.util.config import config, CONFIG_PATH
from pony.orm import OperationalError
from socialserver.util.output import console


# these are used when define_entities
# is called on a database, but pycharm
# isn't aware of that, so we're asking
# it very politely to shut up about
# unused local classes.
# noinspection PyUnusedLocal
def define_entities(db_object):
    class User(db_object.Entity):
        sessions = orm.Set("UserSession")
        display_name = orm.Required(str, max_len=DISPLAY_NAME_MAX_LEN)
        username = orm.Required(str, max_len=USERNAME_MAX_LEN, unique=True)
        password_hash = orm.Required(str)
        password_salt = orm.Required(str)
        creation_time = orm.Required(datetime.datetime)
        birthday = orm.Optional(datetime.date)
        totp = orm.Optional("Totp")
        # legacy accounts are the ones imported from socialserver 2.x during migration
        # this doesn't mean much now, but might become important in the future
        # so might as well have it.
        is_legacy_account = orm.Required(bool)
        # check out AccountAttributes enum in constants for more info
        account_attributes = orm.Required(orm.IntArray)
        bio = orm.Optional(str, max_len=BIO_MAX_LEN)
        posts = orm.Set("Post", cascade_delete=True)
        comments = orm.Set("Comment", cascade_delete=True)
        post_likes = orm.Set("PostLike", cascade_delete=True)
        comment_likes = orm.Set("CommentLike", cascade_delete=True)
        followers = orm.Set("Follow", cascade_delete=True)
        following = orm.Set("Follow", cascade_delete=True)
        blocked_users = orm.Set("Block", cascade_delete=True)
        blocked_by = orm.Set("Block", cascade_delete=True)
        invite_codes = orm.Set("InviteCode", cascade_delete=True)
        profile_pic = orm.Optional("Image")
        header_pic = orm.Optional("Image")
        uploaded_images = orm.Set("Image", reverse="uploader")
        uploaded_videos = orm.Set("Video", reverse="owner")
        # deleting user should leave reports intact
        submitted_reports = orm.Set("PostReport", cascade_delete=False)
        associated_api_keys = orm.Set("ApiKey", cascade_delete=True)
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

        @property
        def totp_enabled(self):
            return self.totp is not None and self.totp.confirmed

    class Totp(db_object.Entity):
        # here as a reverse attribute
        user = orm.Optional("User")
        secret = orm.Required(str)
        # a code will only be used if it's actually confirmed
        confirmed = orm.Required(bool)
        # used for replay attack prevention.
        # optional since it might not always be populated.
        last_used_code = orm.Optional(str)
        creation_time = orm.Required(datetime.datetime)

    class UserSession(db_object.Entity):
        # data collection is for security purposes.
        # need to note that it's not used for advertising.
        # we hash the access token unsalted & hashed with sha256,
        # same as an API key.
        # check ApiKey for a quick explanation of why.
        access_token_hash = orm.Required(str)
        user = orm.Required("User")
        creation_ip = orm.Required(str)
        creation_time = orm.Required(datetime.datetime)
        last_access_time = orm.Required(datetime.datetime)
        user_agent = orm.Required(str)

    class Post(db_object.Entity):
        # whether the post is currently in the mod-queue
        under_moderation = orm.Required(bool)
        user = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        text = orm.Required(str)
        # the reason for this one is purely for relationship reasons,
        # however a set is not of any use for this application;
        # it's unordered, and we want to keep the correct order for
        # images on a post
        images = orm.Set("Image", reverse="associated_posts")
        # this is the useful one instead, since it retains
        # the proper ordering, and can be indexed etc.
        image_ids = orm.Optional(orm.IntArray)
        # need to look into; a post can have photos *OR* videos.
        # can this be enforced with this schema?
        video = orm.Optional("Video")
        comments = orm.Set("Comment", cascade_delete=True)
        likes = orm.Set("PostLike", cascade_delete=True)
        hashtags = orm.Set("Hashtag")
        reports = orm.Set("PostReport", cascade_delete=True)
        # if false, won't show up in feeds. good for if media is incomplete.
        processed = orm.Required(bool)

        @property
        def get_images(self):
            # this helper function will return all image
            # objects using image_ids. the benefit of this
            # over accessing the images property is that
            # this retains the order, and is indexable, since it
            # returns a list.
            images = []
            for i in self.image_ids:
                # noinspection PyUnresolvedAttributeReference
                i_db = db.Image.get(id=i)
                if i_db is not None:
                    images.append(i_db)
            return images

    class PostReport(db_object.Entity):
        # we don't want to just delete these I don't think?
        # better to mark them inactive, until the post is deleted.
        # that way if it's moderated, an admin can still see the acted
        # on report. rather than expose deletion via the API, we should
        # just rely on database constraints to delete reports when the
        # post they are associated with has been removed.
        # IMPORTANT NOTE: could this result in users posting illegal things
        # and then deleting them soon after to prevent reports being seen by a
        # moderator? this needs investigating, but I can't think of a clean
        # solution right now.
        active = orm.Required(bool)
        # we want to ensure that the report has a user,
        # but we don't want to actually tie it to a user,
        # since if somebody reports illegal content, and then
        # deletes their account, we still want to know about
        # the report, so we can take action
        reporter = orm.Optional("User", reverse="submitted_reports")
        post = orm.Required("Post", reverse="reports")
        creation_time = orm.Required(datetime.datetime)
        # since we do one report per post, we want to be able to
        # report multiple infringements at once, hence the array.
        # NOTE: not sure if we do want this? Need to figure that one
        # out soon I guess.
        # check out the socialserver.constants.ReportReasons enum
        # for a list of these.
        report_reason = orm.Required(orm.IntArray)
        supplementary_info = orm.Optional(
            str, max_len=REPORT_SUPPLEMENTARY_INFO_MAX_LEN
        )

    class Image(db_object.Entity):
        uploader = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        # identifier used to retrieve an image object
        identifier = orm.Required(str)
        # sha256 hash of the image, for detecting duplicate uploads.
        sha256_hash = orm.Required(str)
        # identifier used to store the image on disk. can be shared if multiple users
        # post an image with the same SHA256 hash.
        file_identifier = orm.Required(str)
        associated_profile_pics = orm.Set("User", reverse="profile_pic")
        associated_header_pics = orm.Set("User", reverse="header_pic")
        associated_posts = orm.Set("Post", reverse="images")
        associated_thumbnails = orm.Set("Video", reverse="thumbnail")
        blur_hash = orm.Required(str)
        # set to true once the image has been fully processed
        processed = orm.Required(bool)

        @property
        def is_orphan(self):
            return (
                    len(self.associated_posts) == 0
                    and len(self.associated_profile_pics) == 0
                    and len(self.associated_header_pics)
                    and len(self.associated_thumbnails) == 0
            )

    class Hashtag(db_object.Entity):
        creation_time = orm.Required(datetime.datetime)
        name = orm.Required(str, max_len=TAG_MAX_LEN, unique=True)
        posts = orm.Set("Post", reverse="hashtags")

    class PostLike(db_object.Entity):
        user = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        post = orm.Required("Post")

    class CommentLike(db_object.Entity):
        user = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        comment = orm.Required("Comment")

    class Follow(db_object.Entity):
        user = orm.Required("User", reverse="following")
        following = orm.Required("User", reverse="followers")
        creation_time = orm.Required(datetime.datetime)

    class Comment(db_object.Entity):
        user = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        text = orm.Required(str, max_len=COMMENT_MAX_LEN)
        post = orm.Required("Post")
        likes = orm.Set("CommentLike", cascade_delete=True)

    class Block(db_object.Entity):
        user = orm.Required("User", reverse="blocked_users")
        blocking = orm.Required("User", reverse="blocked_by")
        creation_time = orm.Required(datetime.datetime)

    class InviteCode(db_object.Entity):
        user = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        code = orm.Required(str)
        used = orm.Required(bool)

    class ApiKey(db_object.Entity):
        owner = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        # we store this with sha256, not pbkdf2 or argon2,
        # since we want it to be super-fast, as each request
        # will have to verify it if it's in use.
        # no point salting it since it's high entropy already,
        # and practically impossible to build a lookup table for
        key_hash = orm.Required(str)
        permissions = orm.Required(orm.IntArray)  # constants.ApiKeyPermissions

    class Video(db_object.Entity):
        owner = orm.Required("User")
        creation_time = orm.Required(datetime.datetime)
        identifier = orm.Required(str)
        file_identifier = orm.Required(str)
        sha256_hash = orm.Required(str)
        associated_posts = orm.Set("Post", reverse="video")
        thumbnail = orm.Required("Image", reverse="associated_thumbnails")
        # this probably won't be implemented for a while, but
        # if we start transcoding, this will become important.
        processed = orm.Required(bool)


"""
    
    Create a database object bound to an in-memory sqlite database.
    For testing, since data is purged upon app exit.
"""


def create_test_db():
    mem_db = orm.Database()
    define_entities(mem_db)
    mem_db.bind("sqlite", "/tmp/test.db", create_db=True)
    if mem_db.schema is None:
        mem_db.generate_mapping(create_tables=True)
    if mem_db is not None:
        mem_db.drop_all_tables(with_all_data=True)
        mem_db.create_tables()
    return mem_db


"""
    _bind_to_config_specified_db
    
    Binds to the database specified in the configuration file.
    Any connector logic should be put here.
"""


def _bind_to_config_specified_db(db_object):
    # config.database.connector is already validated by pydantic.
    # we don't need to handle an incorrect value here.
    if config.database.connector == "sqlite":
        db_object.bind("sqlite", config.database.filename, create_db=True)
    elif config.database.connector == "postgres":
        try:
            db_object.bind(
                provider="postgres",
                user=config.database.username,
                password=config.database.password,
                host=config.database.host,
                database=config.database.database_name,
            )
        except OperationalError:
            console.log("[bold red]Couldn't connect to database!")
            console.print(
                f"[bold]Please check the configuration file, located at {CONFIG_PATH}!"
            )
            exit()
    db_object.generate_mapping(create_tables=True)


db = orm.Database()
define_entities(db)
_bind_to_config_specified_db(db)
