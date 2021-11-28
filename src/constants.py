from enum import Enum

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
  OG = 6