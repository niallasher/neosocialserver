from socialserver.util.test import test_db, server_address, create_user_session_with_request
import pyotp
import requests
from urllib import parse
from random import randint
from socialserver.constants import LegacyErrorCodes
from socialserver.util.config import config


def test_add_totp_to_account_legacy(test_db, server_address):
    # add totp to the user
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "add",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # legacy api only returns an OTP URL
    otp_url = r.json()['url']
    totp = pyotp.parse_uri(otp_url).now()
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "confirm",
                          "totp": totp
                      })
    assert r.status_code == 201
    # check it's enabled
    r = requests.get(f"{server_address}/api/v2/user/twofactor",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    assert r.json()['enabled'] is True


def test_add_totp_to_account_invalid_verification_legacy(test_db, server_address):
    # add totp to the user
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "add",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # legacy api only returns an OTP URL
    otp_url = r.json()['url']
    totp = pyotp.parse_uri(otp_url).now()
    rand_totp = randint(100000, 999999)
    # yeah it'll never happen,
    # but what if it does?
    while rand_totp == totp:
        rand_totp = randint(100000, 999999)
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "confirm",
                          "totp": rand_totp
                      })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.TOTP_INCORRECT.value
    # TOTP should *not* be enabled in this case!
    r = requests.get(f"{server_address}/api/v2/user/twofactor",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    assert r.json()['enabled'] is False


def test_remove_totp_from_account_legacy(test_db, server_address):
    # add totp to the user
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "add",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # legacy api only returns an OTP URL
    otp_url = r.json()['url']
    totp = pyotp.parse_uri(otp_url).now()
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "confirm",
                          "totp": totp
                      })
    assert r.status_code == 201
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "remove",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # check it's enabled
    r = requests.get(f"{server_address}/api/v2/user/twofactor",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    assert r.json()['enabled'] is False


def test_remove_totp_from_account_without_totp_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "remove",
                          "password": test_db.password
                      })
    assert r.status_code == 400
    assert r.json()['err'] == LegacyErrorCodes.TOTP_NON_EXISTENT_CANNOT_CONFIRM.value


def test_login_totp_legacy(test_db, server_address):
    # add totp to the user
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "add",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # legacy api only returns an OTP URL
    otp_url = r.json()['url']
    totp_object = pyotp.parse_uri(otp_url)
    totp = totp_object.now()
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "confirm",
                          "totp": totp
                      })
    assert r.status_code == 201
    # check it's enabled
    r = requests.get(f"{server_address}/api/v2/user/twofactor",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    assert r.json()['enabled'] is True
    # try to log in without a totp
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": test_db.password
                      })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.TOTP_REQUIRED.value
    r = requests.post(f"{server_address}/api/v1/auth",
                      json={
                          "username": test_db.username,
                          "password": test_db.password,
                          "totp": totp_object.now()
                      })
    assert r.status_code == 200


def test_try_verify_totp_expired_legacy(test_db, server_address):
    config.auth.totp.unconfirmed_expiry_time = 0
    # add totp to the user
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "add",
                          "password": test_db.password
                      })
    assert r.status_code == 201
    # legacy api only returns an OTP URL
    otp_url = r.json()['url']
    totp = pyotp.parse_uri(otp_url).now()
    r = requests.post(f"{server_address}/api/v2/user/twofactor",
                      json={
                          "session_token": test_db.access_token,
                          "action": "confirm",
                          "totp": totp
                      })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.TOTP_INCORRECT.value
    # check it's not enabled
    r = requests.get(f"{server_address}/api/v2/user/twofactor",
                     json={
                         "session_token": test_db.access_token
                     })
    assert r.status_code == 201
    assert r.json()['enabled'] is False
    config.auth.totp.unconfirmed_expiry_time = 300
