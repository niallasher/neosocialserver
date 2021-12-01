from types import SimpleNamespace
from functools import wraps
import argon2
from cryptography.fernet import Fernet
from secrets import randbits
from hashlib import sha256

from pony.orm.core import select
from socialserver.util.config import config
from socialserver.db import DbUserSession
from secrets import token_urlsafe
from pony.orm import db_session

hasher = argon2.PasswordHasher()
fernet_inst = Fernet(config.auth.totp.encryption_key)

"""
    generate_key
    generate a random key. returns the key and it's sha256 hash
    (for storage) in a SimpleNamespace.
    used for API keys and login tokens.
    We just use SHA256 for this; it's fast af, an we need to check
    these with every request to the API.

    No salt is used; these values already have a high entropy
    (i.e. it's near impossible to compute a lookup table for them)
    and we don't want to take any longer than we have to to verify
    them
"""


def generate_key() -> SimpleNamespace(key=str, hash=str):
    # 32 random bytes. sufficently secure, not too big payload-wise
    # if we send it with each request
    key = token_urlsafe(32)
    return SimpleNamespace(
        key=key,
        hash=sha256(key.encode()).hexdigest()
    )


"""
    verify_plaintext_against_hash_sha256
    verify that plaintext matches a provided hash
    (use this to check auth token and api key hashes)
"""


def verify_plaintext_against_hash_sha256(plaintext, hash) -> bool:
    return sha256(plaintext.encode()).hexdigest() == hash


"""
    legacy_generate_salt
    generate a 2.x format salt. this should never be needed,
    but in case of unforseen circumstances, it's here
"""


def legacy_generate_salt() -> str:
    # NOTE: any migrated account will have one of these
    # old format salts, however, it's stored in the database,
    # and it doesn't make a difference to the verify function,
    # which is compatible anyway
    salt_basis = randbits(128).__str__().encode()
    return sha256(salt_basis).hexdigest()


"""
    generate_salt
    return a random token, appended to a password to prevent precomputed tables
    in the event of a database leak
"""


def generate_salt() -> str:
    return token_urlsafe(32)


"""
    hash_password
    hash a password with a salt. you can generate a salt using
    generate_salt()
"""


def hash_password(plaintext, salt) -> str:
    assembled_password = plaintext + salt
    return hasher.hash(assembled_password)


"""
    verify_password_valid
    take a plaintext password and a hash, and verify that the password is ok

"""


def verify_password_valid(plaintext, salt, hash) -> bool:
    try:
        return hasher.verify(hash, plaintext + salt)
    except argon2.exceptions.VerifyMismatchError:
        return False


"""
    hash_plaintext_sha256
    hash plaintext with the sha256 algo
"""


def hash_plaintext_sha256(plaintext):
    return sha256(plaintext.encode()).hexdigest()


"""
    get_user_from_session
    Returns [user, session] if session is valid. Otherwise raises an exception.
"""


@db_session
def get_username_from_token(session_token):
    print(
        hash_plaintext_sha256(session_token)
    )
    existing_session = DbUserSession.get(
        access_token_hash=hash_plaintext_sha256(session_token))
    if existing_session is not None:
        return existing_session.user
    raise Exception("Invalid session token")


"""
    get_ip_from_request
    returns the ip address of the requester, handles reverse proxy (if proxy configured correctly!)
"""


def get_ip_from_request(request):
    ip = request.headers.get('X-Forwarded-For')
    if ip is None:
        ip = request.remote_addr
    return ip


# TODO: fix this stuff

# def fernet_encrypt_string(string) -> str:
#     return fernet_inst.encrypt(string.encode()).decode()


# def fernet_decrypt_string(string) -> str:
#     return fernet_inst.decrypt(string.encode())


# test that hashing works ok if running from the command line
if __name__ == "__main__":
    print(" --= argon2 hashing =-- ")
    plaintext = "hello world"
    salt = generate_salt()
    hash = hash_password(plaintext, salt)
    print(f"plaintext: {plaintext}")
    print(f"salt: {salt}")
    print(f"hash: {hash}")
    print(f"verify: {verify_password_valid(plaintext, salt, hash)}")
    print(f"invalid verify: {verify_password_valid('lolnope', salt, hash)}")
