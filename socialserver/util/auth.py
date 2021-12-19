from types import SimpleNamespace
import argon2
from cryptography.fernet import Fernet
from secrets import randbits
from hashlib import sha256

from socialserver.util.oldconfig import config
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
    # 32 random bytes. sufficiently secure, not too big payload-wise
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


def verify_plaintext_against_hash_sha256(plaintext: str, given_hash: str) -> bool:
    return sha256(plaintext.encode()).hexdigest() == given_hash


"""
    legacy_generate_salt
    generate a 2.x format salt. this should never be needed,
    but in case of unforeseen circumstances, it's here
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


def hash_password(plaintext: str, salt: str) -> str:
    assembled_password = plaintext + salt
    return hasher.hash(assembled_password)


"""
    verify_password_valid
    take a plaintext password and a hash, and verify that the password is ok

"""


def verify_password_valid(plaintext: str, salt: str, given_hash: str) -> bool:
    try:
        return hasher.verify(given_hash, plaintext + salt)
    except argon2.exceptions.VerifyMismatchError:
        return False


"""
    hash_plaintext_sha256
    hash plaintext with the sha256 algo
"""


def hash_plaintext_sha256(plaintext: str) -> str:
    return sha256(plaintext.encode()).hexdigest()


"""
    get_username_from_token
    returns a username if a session token is valid, otherwise none
"""


@db_session
def get_username_from_token(session_token: str) -> str or None:
    existing_session = DbUserSession.get(
        access_token_hash=hash_plaintext_sha256(session_token))
    if existing_session is not None:
        return existing_session.user.username
    else:
        return None


"""
    get_ip_from_request
    returns the ip address of the requester, handles reverse proxy (if proxy configured correctly!)
"""


def get_ip_from_request(request) -> str:
    ip = request.headers.get('X-Forwarded-For')
    if ip is None:
        ip = request.remote_addr
    return ip


# TODO: fix this stuff

# def fernet_encrypt_string(string) -> str:
#     return fernet_inst.encrypt(string.encode()).decode()


# def fernet_decrypt_string(string) -> str:
#     return fernet_inst.decrypt(string.encode())
