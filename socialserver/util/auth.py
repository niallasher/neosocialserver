from functools import wraps
from types import SimpleNamespace
import argon2
from secrets import randbits
from hashlib import sha256
from secrets import token_urlsafe
from pony.orm import db_session
from socialserver.db import db
from flask import abort, request, make_response, jsonify
from socialserver.constants import ErrorCodes

import pony.orm

hasher = argon2.PasswordHasher()

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


def get_username_from_token(session_token: str, db) -> str or None:
    # note: we don't need or want a db_session here, since
    # anything calling it will already have to be wrapped in
    # one, which extends down to here.
    existing_session = db.UserSession.get(
        access_token_hash=hash_plaintext_sha256(session_token))
    if existing_session is not None:
        return existing_session.user.username
    else:
        return None


"""
    get_user_object_from_token
    returns an object representing the user in the database, or None if no match found
"""


# TODO: figure out how to type a pony database entity
def get_user_object_from_token(session_token: str, db: pony.orm.Database):
    existing_session = db.UserSession.get(
        access_token_hash=hash_plaintext_sha256(session_token))
    if existing_session is not None:
        return existing_session.user
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


"""
    auth_reqd
    
    Decorator for any resources that require auth.
    It will validate whether a token is correct.
"""


def auth_reqd(f):
    @wraps(f)
    @db_session
    def decorated_function(*args, **kwargs):
        headers = request.headers
        headers.get("Authorization") or abort(
            make_response(jsonify(
                error=ErrorCodes.AUTHORIZATION_HEADER_NOT_PRESENT.value
            ), 401))
        auth_token = headers.get("Authorization").split(" ")[1]
        existing_entry = db.UserSession.get(
            access_token_hash=hash_plaintext_sha256(auth_token))
        if existing_entry is None:
            abort(
                make_response(jsonify(
                    error=ErrorCodes.TOKEN_INVALID.value
                ), 401))
        return f(*args, **kwargs)

    return decorated_function
