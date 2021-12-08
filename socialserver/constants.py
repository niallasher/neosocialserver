from enum import Enum

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
# client should round up to the next integer, but we'll do it if they dont.
MAX_PIXEL_RATIO = 4
MAX_IMAGE_SIZE_POST = (1500, 1500)
MAX_IMAGE_SIZE_POST_PREVIEW = (256, 256)
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
    # might even get a tab in the mobile app for some cleanup tasks?
    # basically could be aliases to GOD_EMPEROR, but that's a bit of a stretch.


"""
  ErrorCodes
  A list of error codes, to increase code readability.
"""


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
  Note these are seperate from ImageTypes, since
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
  for imageutil.save_images_to_disk
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
  Regex expressions for validating data.
"""

# only alphanumerics and _, from 1 to 20 letters.
REGEX_USERNAME_VALID = r"^[a-z0-9_]{1," + USERNAME_MAX_LEN.__str__() + r"}$"
# split out hashtags
REGEX_HASHTAG = r"#[a-zA-Z0-9]{1,12}"
