#  Copyright (c) Niall Asher 2022

from enum import Enum
from os import path

# root directory of the module where-ever it happens to be running.
ROOT_DIR = path.dirname(path.abspath(__file__))

# semver spec.
# major/minor/patch.
# any breaking changes, or the introduction
# of a new version of the API must bump the
# major version number (post API freeze when
# 3.0.0 releases)
# new feature introductions can be in a minor,
# even if they change the current api, AS LONG
# AS THEY DO NOT BREAK CLIENT COMPATIBILITY!
SERVER_VERSION = "3.0.0"

# the interval to wait between each check of the unprocessed
# post queue, in seconds.
UNPROCESSED_POST_CHECK_INTERVAL = 10

# The blurhash to use during image processing.
# 000000 is just plain black.
PROCESSING_BLURHASH = "000000"

"""
    Video Stuff (WIP)
"""
MAX_VIDEO_SIZE_MB = 50
# we're literally just using direct play for now,
# so keep this lean. in the future, we could use celery or smth
# to process the video into a proper format?
VIDEO_SUPPORTED_FORMATS = ["video/mp4", "video/quicktime"]

"""
  Max string length for different user generated areas.
"""
DISPLAY_NAME_MAX_LEN = 32
USERNAME_MAX_LEN = 20
BIO_MAX_LEN = 256
POST_MAX_LEN = 256
TAG_MAX_LEN = 12
REPORT_SUPPLEMENTARY_INFO_MAX_LEN = 256
COMMENT_MAX_LEN = 256
# these aren't able to be enforced by the db or anything,
# since we store an argon2 hash. this is just for enforcing
# quality when a user is creating an account.
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 256
MAX_FEED_GET_COUNT = 32

"""
  Maximum amounts of attribs per post
  Not enforced by the database, make doubly sure the API doesn't break
"""
MAX_IMAGES_PER_POST = 4
MAX_TAGS_PER_POST = 5

"""
  Image sizing
  These still
"""

# highest pixel ratio we generate. anything higher will be given the max.
# client should round up to the next integer, but we'll do it if they don't.
MAX_PIXEL_RATIO = 4
MAX_IMAGE_SIZE_POST = (3000, 3000)
MAX_IMAGE_SIZE_POST_PREVIEW = (512, 512)
MAX_IMAGE_SIZE_PROFILE_PICTURE = (64, 64)
MAX_IMAGE_SIZE_PROFILE_PICTURE_LARGE = (128, 128)
MAX_IMAGE_SIZE_HEADER = (600, 400)
MAX_IMAGE_SIZE_GALLERY_PREVIEW = (256, 256)

"""
  AccountAttributes
  A list of modifiers and accolades for an account.
"""


class AccountAttributes(Enum):
    VERIFIED = 0
    ADMIN = 1
    MODERATOR = 2
    BANNED = 3
    PRIVATE = 4
    BETA_TESTER = 5
    OG = 6  # user since socialshare pre-1.0. what a legend.
    INSTANCE_ADMIN = 7  # can control webui when it's added.
    CAN_INVITE_USERS = 8  # any account with this gets access to invite codes,
    # if config.auth.registration.invite_only.restrict_invites is True.


"""
  RegistrationType
  The different restrictions that can be applied
  to registration.
"""


class RegistrationType(Enum):
    REGISTRATION_DISABLED = 0
    NO_RESTRICTION = 1
    INVITE_ONLY = 2
    APPROVAL_REQUIRED = 3


"""
  ErrorCodes
  A list of error codes, to increase code readability.
"""


# TODO: clean up these. all not found errors should be generic OBJECT_NOT_FOUND or smth!
class ErrorCodes(Enum):
    PASSWORD_DAMAGED = 1
    TOTP_REQUIRED = 2
    TOTP_INCORRECT = 3
    TOTP_DAMAGED = 4
    IMAGE_TO_BIG = 5
    IMAGE_UPLOAD_FAILED = 6
    CONNECTION_ERROR = 7
    USER_BANNED = 8
    USER_BLOCKED = 9
    USERNAME_INVALID = 10
    USERNAME_TAKEN = 11
    USERNAME_NOT_FOUND = 12
    TAG_INVALID = 13
    ACTION_FAILED = 14
    MALFORMED_CONTENT = 15
    TOKEN_REVOKED = 16
    TOKEN_INVALID = 17
    TOKEN_ASSIGNMENT_FAILED = 18
    TOKEN_REVOKE_FAILED = 19
    POST_INVALID = 20
    API_KEY_INVALID = 21
    PASSWORD_NON_CONFORMING = 22
    BIO_NON_CONFORMING = 23
    DISPLAY_NAME_NON_CONFORMING = 24
    POST_NOT_FOUND = 25
    POST_TOO_MANY_IMAGES = 26
    IMAGE_NOT_FOUND = 27
    POST_TOO_LONG = 28
    FEED_GET_COUNT_TOO_HIGH = 29
    INCORRECT_PASSWORD = 30
    INVALID_USER_MODIFICATION_OPTION = 31
    USER_MODIFICATION_NO_OPTIONS_GIVEN = 32
    IMAGE_TYPE_INVALID = 33
    FOLLOW_ALREADY_EXISTS = 34
    CANNOT_FOLLOW_SELF = 35
    CANNOT_FIND_FOLLOW_ENTRY = 36
    BLOCK_ALREADY_EXISTS = 37
    CANNOT_BLOCK_SELF = 38
    CANNOT_FIND_BLOCK_ENTRY = 39
    # I'm not sure whether it's a good idea to limit
    # reports per post, but I think it will help reduce spam?
    # although, I am not sure if we want to reveal to the user that
    # their report didn't go through since they already have;
    # this could just encourage them to create a new account and
    # report again? maybe this should be a config key, since it
    # seems like a personal choice r.e. balance of transparency
    # and preventing spam?
    POST_ALREADY_REPORTED = 40
    POST_REPORT_REASON_INVALID = 41
    # yes, I am aware of the irony involved in the name
    # of this error being so long :)
    POST_REPORT_SUPPLEMENTAL_INFO_TOO_LONG = 42
    # I feel like there is no reason to do this, so we might
    # as well disallow it. might change later.
    CANNOT_REPORT_OWN_POST = 43
    USER_NOT_MODERATOR_OR_ADMIN = 44
    REPORT_NOT_FOUND = 45
    ACCOUNT_NOT_APPROVED = 46
    AUTHORIZATION_HEADER_NOT_PRESENT = 47
    INVALID_IMAGE_PACKAGE = 48
    TOTP_ALREADY_ACTIVE = 49
    TOTP_NOT_ACTIVE = 50
    TOTP_EXPENDED = 51
    USER_NOT_ADMIN = 52
    INVALID_SORT_TYPE = 53
    USER_ALREADY_APPROVED = 54
    COMMENT_TOO_LONG = 55
    COMMENT_TOO_SHORT = 56
    COMMENT_NOT_FOUND = 57
    OBJECT_NOT_OWNED_BY_USER = 58
    OBJECT_NOT_LIKED = 59
    OBJECT_ALREADY_LIKED = 60
    REQUEST_TOO_LARGE = 61
    INVALID_VIDEO = 62
    OBJECT_NOT_FOUND = 63
    IMAGE_NOT_PROCESSED = 64
    POST_NOT_PROCESSED = 65
    INVALID_IMAGE_FORMAT = 66
    INVALID_ATTACHMENT_ENTRY = 67
    # when the same media entry is provided twice.
    # the same media can be in a post multiple times,
    # but not the same entry (i.e.: it can be uploaded twice)
    DUPLICATE_MEDIA_IN_POST = 68


"""
    LegacyErrorCodes
    
    Error codes for old API compatibility reasons reasons
    Invite codes are commented out for now, since I'm not sure
    whether they'll make their way to the new server.
"""


class LegacyErrorCodes(Enum):
    IMAGE_NOT_FOUND = "I01"
    TOKEN_INVALID = "A01"
    # INVITE_CODE_INVALID = "A02"
    # INVITE_CODE_USED = "A03"
    TOTP_REQUIRED = "A04"
    TOTP_INCORRECT = "A05"
    TOTP_ALREADY_ADDED = "A06"
    TOTP_ALREADY_REMOVED_OR_NOT_PRESENT = "A07"
    INVALID_ACTION_FIELD_ON_TOTP_POST_CALL = "A08"
    TOTP_NON_EXISTENT_CANNOT_CONFIRM = "A09"
    INCORRECT_PASSWORD = "PA01"
    PASSWORD_NON_CONFORMING = "PA02"
    PASSWORD_DAMAGED = "PA03"
    USER_NOT_ADMIN = "AC01"
    INSUFFICIENT_PERMISSIONS_TO_MODIFY_USER_DESTRUCTIVE = "AC02"
    USERNAME_NOT_FOUND = "U01"
    USERNAME_TAKEN = "U02"
    POST_NOT_FOUND = "P01"
    INSUFFICIENT_PERMISSIONS_TO_VIEW_POST = "P02"
    INSUFFICIENT_PERMISSIONS_TO_ACCESS_MODQUEUE = "MQ01"
    GENERIC_SERVER_ERROR = "GS01"


"""
    LegacyAdminUserModTypes
    
    Enum containing valid legacy admin usermod operations
"""


class LegacyAdminUserModTypes(Enum):
    VERIFICATION_STATUS = "verified"
    MODERATOR_STATUS = "moderator"


"""
  ReportReasons
  A list of reasons to report a post
"""


class ReportReasons(Enum):
    SPAM = 0
    OFFENSIVE = 1
    DISCRIMINATION = 2
    ILLEGAL_CONTENT = 3
    OTHER = 4


"""
  ApiKeyPermissions
  A list of permissions for an API key.
"""


class ApiKeyPermissions(Enum):
    READ = 0  # read only access to the socialshare api.
    POST = 1  # can post comments, posts and upload images
    MODIFY_FOLLOWERS = 2  # can add/remove followers
    MODIFY_ACCOUNT_SETTINGS = 3  # can change account settings
    ACCESS_MODERATION = 4  # can access the moderation zone
    ACCESS_ADMIN = 5  # can access the admin zone
    DELETE_ACCOUNT = 6  # can delete the account (still requires a password)


"""
  ImageUploadTypes
  A list of image upload types. Used to define
  what the size of the image should be.
  Note these are separate from ImageTypes, since
  they can define multiple images (e.g. profile picture, and profile picture large). While ImageTypes
  represent a single one.
"""


class ImageUploadTypes(Enum):
    POST = 0
    HEADER = 1
    PROFILE_PICTURE = 2


"""
  ImageTypes
  A list of imageset save types and their respective filenames,
  for socialserver.util.image.save_images_to_disk
"""


class ImageTypes(Enum):
    GALLERY_PREVIEW = "gal-prev"
    POST_PREVIEW = "post-prev"
    POST = "post"
    PROFILE_PICTURE = "prof-pic"
    PROFILE_PICTURE_LARGE = "prof-pic-l"
    HEADER = "header"
    ORIGINAL = "orig"


"""
  ApprovalSortTypes
  A list of sort types for the user approval queue
"""


class ApprovalSortTypes(Enum):
    CREATION_TIME_ASCENDING = 0
    CREATION_TIME_DESCENDING = 1
    USERNAME_ALPHABETICAL = 2
    DISPLAY_NAME_ALPHABETICAL = 3


"""
    CommentFeedSortTypes
    A list of sort types for the comment feed. Might include post feeds eventually too.
"""


class CommentFeedSortTypes(Enum):
    CREATION_TIME_DESCENDING = 0
    LIKE_COUNT = 1


"""
  UserModificationOptions
  A list of user options that can be modified using
  only a token. Authentication requires active
  re-auth to change, so it isn't included here
"""

UserModificationOptions = [
    "display_name",
    "username",
    "bio",
    "profile_pic_reference",
    "header_pic_reference",
]

"""
  UserAuthenticationModificationOptions
  A list of user authentication options.
  Just passwords until TOTP gets re-implemented.
  (All options here will require explict re-authentication
  from the user.)
"""

UserAuthenticationModificationOptions = ["password"]

"""
  ImageSupportedMimeTypes
  A list of image formats supported for upload,
  in MIME type form. These have to be supported
  by PIL, and we convert them all to jpg anyway.
  Possible future idea: WebP serving support?
  The client can just tell us to use it if it
  detects support on it's platform?

  ALSO: need to investigate HEIC, namely, does iOS
  give us a HEIC image when doing an image upload?
  if so we'll need to handle that.
  pillow-heic is a thing i think?
  for now, lets not support it.
"""

ImageSupportedMimeTypes = [
    "image/bmp",
    "image/gif",
    # .ico WHY WOULD PEOPLE USE THIS????
    # pil supports it so we'll keep it for now
    "image/x-icon",
    "image/jpg",
    "image/jpeg",
    # jpeg 2000
    "image/jp2",
    "image/png",
    "image/webp",
    "image/tiff",
]

"""
  Regex expressions for validating data.
"""

# only alphanumerics and _, from 1 to 20 letters.
REGEX_USERNAME_VALID = r"^[a-z0-9_]{1," + USERNAME_MAX_LEN.__str__() + r"}$"
# split out hashtags
REGEX_HASHTAG = r"#[a-zA-Z0-9]{1,12}"

"""
    Values for BlurHash encoding
    Each must be >= 1 and <= 9
"""

BLURHASH_X_COMPONENTS = 4
BLURHASH_Y_COMPONENTS = 3

"""
    post media types, to send to the client.
    e.g. images, videos etc.
"""


class PostAdditionalContentTypes(Enum):
    NONE = 0
    IMAGES = 1
    VIDEO = 2
    POLL = 3


""" 
    sort types for follow lists
"""


class FollowListSortTypes(Enum):
    AGE_ASCENDING = 0
    AGE_DESCENDING = 1


"""
    the type of follow(er||ing) information to get
    internal. no need for the api to utilize this!
"""


class FollowListListTypes(Enum):
    FOLLOWERS = 0
    FOLLOWING = 1


# Exceptions

# pretty self-explanatory
class UserNotFoundException(Exception):
    pass


"""
    SERVER_SUPPORTED_IMAGE_FORMATS
    Formats that an image can be delivered in.
    Makes no guarantee that they're enabled, or that any specific image has them,
    just that they're technically supported.
"""


class ServerSupportedImageFormats(Enum):
    WEBP = "webp"
    JPG = "jpg"


"""
    SERVER_SUPPORTED_IMAGE_FORMATS_MIMETYPES
    Pretty self explanatory
"""

SERVER_SUPPORTED_IMAGE_FORMATS_MIMETYPES = {
    "webp": "image/webp",
    "jpg": "image/jpg"
}
