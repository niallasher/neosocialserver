# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, set_user_attributes_db, create_user_with_request, server_address
from socialserver.constants import AccountAttributes, LegacyErrorCodes, LegacyAdminUserModTypes
import requests


def test_toggle_verification_status_on_user_legacy(test_db, server_address):
    # make test user an admin
    set_user_attributes_db(test_db.db,
                           username="test",
                           attributes=[AccountAttributes.ADMIN.value])

    create_user_with_request(server_address, username="test2", password="password")

    # verify the user
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.VERIFICATION_STATUS.value,
                          "username": "test2"
                      })

    assert r.status_code == 201

    # get info and check they're verified now
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "test2"
                     })

    assert r.json()['isVerified'] is True
    assert r.status_code == 200

    # now undo it!
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.VERIFICATION_STATUS.value,
                          "username": "test2"
                      })

    assert r.status_code == 201

    # get info and check they're no longer verified
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "test2"
                     })
    assert r.json()['isVerified'] is False
    assert r.status_code == 200


def test_toggle_moderation_status_on_user_legacy(test_db, server_address):
    # make test user an admin
    set_user_attributes_db(test_db.db,
                           username="test",
                           attributes=[AccountAttributes.ADMIN.value])

    create_user_with_request(server_address, username="test2", password="password")

    # verify the user
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.MODERATOR_STATUS.value,
                          "username": "test2"
                      })

    assert r.status_code == 201

    # get info and check they're verified now
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "test2"
                     })

    assert r.json()['isModerator'] is True
    assert r.status_code == 200

    # now undo it!
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.MODERATOR_STATUS.value,
                          "username": "test2"
                      })

    assert r.status_code == 201

    # get info and check they're no longer verified
    r = requests.get(f"{server_address}/api/v1/users",
                     json={
                         "session_token": test_db.access_token,
                         "username": "test2"
                     })
    assert r.json()['isModerator'] is False
    assert r.status_code == 200


def test_attempt_admin_mod_insufficient_perms_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.VERIFICATION_STATUS.value,
                          "username": test_db.username
                      })
    assert r.status_code == 401
    assert r.json()['err'] == LegacyErrorCodes.USER_NOT_ADMIN.value


def test_attempt_admin_mod_invalid_username_legacy(test_db, server_address):
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": LegacyAdminUserModTypes.VERIFICATION_STATUS.value,
                          "username": "does_not_exist"
                      })
    assert r.status_code == 404


def test_attempt_admin_mod_invalid_modtype_legacy(test_db, server_address):
    set_user_attributes_db(test_db.db,
                           test_db.username,
                           [AccountAttributes.ADMIN.value])
    r = requests.post(f"{server_address}/api/v1/admin/usermod",
                      json={
                          "session_token": test_db.access_token,
                          "modtype": "definitely_invalid",
                          "username": test_db.username
                      })
    # this is supposed to be 500. the old server returned 500,
    # so the compatibility stuff requires this :(
    assert r.status_code == 500
