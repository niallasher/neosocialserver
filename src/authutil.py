from types import SimpleNamespace
import argon2
from cryptography.fernet import Fernet
from secrets import randbits, randbytes
from hashlib import sha256
from configutil import config
from secrets import token_urlsafe

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


def generate_key():
    # 32 random bytes. sufficently secure, not too big payload-wise
    # if we send it with each request
    key = token_urlsafe(32)
    return SimpleNamespace(
        key=key,
        hash=sha256(key.encode()).hexdigest()
    )


def generate_salt() -> str:
    salt_basis = randbits(128).__str__().encode()
    # yes, this is longer than any salt need be,
    # but socialshare used this, so we need compat for passwords.
    # might introduce a new password requirement later?
    return sha256(salt_basis).hexdigest()


def hash_password(plaintext, salt) -> str:
    assembled_password = plaintext + salt
    return hasher.hash(assembled_password)


def verify_password_valid(plaintext, salt, hash) -> bool:
    try:
        return hasher.verify(hash, plaintext + salt)
    except argon2.exceptions.VerifyMismatchError:
        return False

# TODO: fix this stuff

# def fernet_encrypt_string(string) -> str:
#     return fernet_inst.encrypt(string.encode()).decode()


# def fernet_decrypt_string(string) -> str:
#     return fernet_inst.decrypt(string.encode())


if __name__ == "__main__":
    # test pw stuff
    print(" --= argon2 hashing =-- ")
    plaintext = "hello world"
    salt = generate_salt()
    hash = hash_password(plaintext, salt)
    print(f"plaintext: {plaintext}")
    print(f"salt: {salt}")
    print(f"hash: {hash}")
    print(f"verify: {verify_password_valid(plaintext, salt, hash)}")
    print(f"invalid verify: {verify_password_valid('lolnope', salt, hash)}")
