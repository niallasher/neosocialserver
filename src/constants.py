from enum import Enum

DISPLAY_NAME_MAX_LEN = 32
USERNAME_MAX_LEN = 20
BIO_MAX_LEN = 256
POST_MAX_LEN = 256
TAG_MAX_LEN = 12
REPORT_SUPPLEMENTARY_INFO_MAX_LEN = 256
COMMENT_MAX_LEN = 256
# these two aren't enforeced by the database.
# need to check whenever somebody makes a new post.
MAX_IMAGES_PER_POST = 4
MAX_TAGS_PER_POST = 5


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
    INCORRECT_PASSWORD = 0
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
