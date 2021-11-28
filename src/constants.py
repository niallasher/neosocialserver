from enum import Enum


USERNAME_MAX_LEN = 20
BIO_MAX_LEN = 256
POST_MAX_LEN = 256
TAG_MAX_LEN = 12
MAX_IMAGES_PER_POST = 4


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
  OG = 6 # user since socialshare pre-1.0. what a legend.
  INSTANCE_ADMIN = 7  # can control webui when it's added.
                      # might even get a tab in the mobile app for some cleanup tasks?
                      # basically could be aliases to GOD_EMPEROR, but that's a bit of a stretch.