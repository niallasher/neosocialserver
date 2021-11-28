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
  ReportReasons
  A list of reasons to report a post
"""


class ReportReasons(Enum):
    SPAM = 0
    OFFENSIVE = 1
    DISCRIMINATION = 2
    ILLEGAL_CONTENT = 3
    OTHER = 4
