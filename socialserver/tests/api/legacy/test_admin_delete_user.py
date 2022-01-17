from socialserver.util.test import test_db, server_address, set_user_attributes_db, create_user_with_request, \
    create_user_session_with_request, create_post_with_request
from socialserver.constants import AccountAttributes, LegacyErrorCodes
import requests


def test_delete_user_admin_legacy(test_db, server_address):
    # make the test user an administrator
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    # create a user to unfairly obliterate
    create_user_with_request(server_address, username="unwitting_victim", password="password")
    # destroy the aforementioned user with extreme prejudice
    r = requests.delete(f"{server_address}/api/v1/admin/userdel",
                        json={
                            "session_token": test_db.access_token,
                            "username": "unwitting_victim",
                            "password": test_db.password
                        })
    assert r.status_code == 201
    # double check that the user is gone for good.
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "unwitting_victim"
                     })
    assert r.status_code == 404


def test_delete_user_admin_insufficient_perms_legacy(test_db, server_address):
    # create a user to unfairly obliterate
    create_user_with_request(server_address, username="unwitting_victim", password="password")
    # attempt to destroy the aforementioned user with extreme prejudice
    r = requests.delete(f"{server_address}/api/v1/admin/userdel",
                        json={
                            "session_token": test_db.access_token,
                            "username": "unwitting_victim",
                            "password": test_db.password
                        })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.USER_NOT_ADMIN.value
    # double check that the user is still around.
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "unwitting_victim"
                     })
    assert r.status_code == 200


def test_delete_user_admin_invalid_username_legacy(test_db, server_address):
    # make the test user an administrator
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    # try to destroy a non-existent user with a moderate level of prejudice
    r = requests.delete(f"{server_address}/api/v1/admin/userdel",
                        json={
                            "session_token": test_db.access_token,
                            "username": "non_existent_user",
                            "password": test_db.password
                        })
    # wrong error return code, but it's how the original server did things,
    # and we're sadly beholden to that.
    assert r.status_code == 401


def test_delete_user_admin_invalid_password_legacy(test_db, server_address):
    # make the test user an administrator
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    # create a user to unfairly obliterate
    create_user_with_request(server_address, username="unwitting_victim", password="password")
    # destroy the aforementioned user with literally no prejudice
    r = requests.delete(f"{server_address}/api/v1/admin/userdel",
                        json={
                            "session_token": test_db.access_token,
                            "username": "unwitting_victim",
                            "password": "hunter2"
                        })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.INCORRECT_PASSWORD.value
    # double check that the user is safe (for now)
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "unwitting_victim"
                     })
    assert r.status_code == 200


def test_attempt_delete_other_admin_admin_legacy(test_db, server_address):
    # make the test user an administrator
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    # create a user to unfairly obliterate, (except this time they're an admin)
    # (is it obvious these tests are copied and pasted with some comment alterations?)
    create_user_with_request(server_address, username="unwitting_victim", password="password")
    set_user_attributes_db(test_db.db,
                           "unwitting_victim",
                           [AccountAttributes.ADMIN.value])
    # destroy the aforementioned user with extreme prejudice
    r = requests.delete(f"{server_address}/api/v1/admin/userdel",
                        json={
                            "session_token": test_db.access_token,
                            "username": "unwitting_victim",
                            "password": test_db.password
                        })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.INSUFFICIENT_PERMISSIONS_TO_MODIFY_USER_DESTRUCTIVE.value
    # double check that the user isn't gone for good.
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "unwitting_victim"
                     })
    assert r.status_code == 200
