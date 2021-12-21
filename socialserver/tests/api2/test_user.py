# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.tests.util import test_db, server_address, test_db_with_user
import requests
from pony.orm import db_session
from socialserver.constants import ErrorCodes, BIO_MAX_LEN, DISPLAY_NAME_MAX_LEN
from secrets import token_urlsafe


def test_create_user(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)

    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                          })
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 201
    test_db.drop_all_tables(with_all_data=True)


def test_create_user_with_bio(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": "something goes here"
                                          })
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_bio_too_long(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                              "bio": token_urlsafe(BIO_MAX_LEN + 1)
                                          })
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.BIO_NON_CONFORMING.value


@db_session
def test_attempt_create_duplicate_user(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    requests.post(f"{server_address}/api/v2/user",
                  json={
                      "display_name": "Test User",
                      "username": "test",
                      "password": "password",
                  })
    user_creation_request = requests.post(f"{server_address}/api/v2/user",
                                          json={
                                              "display_name": "Test User",
                                              "username": "test",
                                              "password": "password",
                                          })
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()['error'] == ErrorCodes.USERNAME_TAKEN.value


def test_create_user_missing_args(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    assert requests.post(f"{server_address}/api/v2/user", json={}).status_code == 400


def test_create_user_username_too_long(test_db, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db)
    invalid_req = requests.post(f"{server_address}/api/v2/user",
                                json={
                                    "display_name": "Test User",
                                    "username": "idontknowwhattoputherebutitsgottabelong",
                                    "password": "password",
                                })
    assert invalid_req.status_code == 400
    assert invalid_req.json()['error'] == ErrorCodes.USERNAME_INVALID.value


def test_delete_user(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.delete(f"{server_address}/api/v2/user",
                              json={
                                  "access_token": test_db_with_user.get('access_token'),
                                  "password": test_db_with_user.get('password')
                              })
    print(del_req.json())
    assert del_req.status_code == 200


def test_delete_user_invalid_password(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.delete(f"{server_address}/api/v2/user",
                              json={
                                  "access_token": test_db_with_user.get('access_token'),
                                  "password": "defo_not_the_right_password"
                              })
    print(del_req.json())
    assert del_req.status_code == 401
    assert del_req.json()['error'] == ErrorCodes.INCORRECT_PASSWORD.value


def test_delete_user_missing_input(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.delete(f"{server_address}/api/v2/user",
                              json={})
    assert del_req.status_code == 400


def test_delete_user_invalid_token(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.delete(f"{server_address}/api/v2/user",
                              json={
                                  "access_token": 'not_even_valid_form',
                                  "password": test_db_with_user.get('password')
                              })
    print(del_req.json())
    assert del_req.status_code == 401
    assert del_req.json()['error'] == ErrorCodes.TOKEN_INVALID.value


def test_update_username(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "username": "validusername"
                             })
    print(del_req.json())
    assert del_req.status_code == 200
    assert del_req.json()['username'] == 'validusername'


def test_update_username_invalid(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))
    print(test_db_with_user.get('access_token'))
    del_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "username": "defonotavalidusernamecuzitswaytoolong"
                             })
    print(del_req.json())
    assert del_req.status_code == 400
    assert del_req.json()['error'] == ErrorCodes.USERNAME_INVALID.value


def test_update_username_already_exists(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    # create a second user, so we can try to steal its name
    requests.post(f"{server_address}/api/v2/user",
                  json={
                      "display_name": "Test User 2",
                      "username": "test2",
                      "password": "password",
                  })

    del_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "username": "test2"
                             })
    print(del_req.json())
    assert del_req.status_code == 400
    assert del_req.json()['error'] == ErrorCodes.USERNAME_TAKEN.value


def test_update_username_missing_input(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    patch_req = requests.patch(f"{server_address}/api/v2/user", json={})
    print(patch_req.json())
    assert patch_req.status_code == 400


def test_update_bio(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "bio": "this is the new bio content 😀"
                             })
    assert bio_req.status_code == 201


def test_update_bio_missing_input(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user", json={})
    assert bio_req.status_code == 400


def test_update_bio_too_long(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "bio": token_urlsafe(BIO_MAX_LEN + 1)
                             })

    assert bio_req.status_code == 400
    assert bio_req.json()['error'] == ErrorCodes.BIO_NON_CONFORMING.value


def test_update_display_name(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "display_name": "new name"
                             })

    assert bio_req.status_code == 201
    assert bio_req.json()['display_name'] == 'new name'


def test_update_display_name_missing_input(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={})

    assert bio_req.status_code == 400


def test_update_display_name_too_long(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token'),
                                 "display_name": token_urlsafe(DISPLAY_NAME_MAX_LEN + 1)
                             })

    assert bio_req.status_code == 400
    assert bio_req.json()['error'] == ErrorCodes.DISPLAY_NAME_NON_CONFORMING.value


def test_update_no_mod_params(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    bio_req = requests.patch(f"{server_address}/api/v2/user",
                             json={
                                 "access_token": test_db_with_user.get('access_token')
                             })

    assert bio_req.status_code == 400
    assert bio_req.json()['error'] == ErrorCodes.USER_MODIFICATION_NO_OPTIONS_GIVEN.value


def test_get_user_info(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    info_req = requests.get(f"{server_address}/api/v2/user/info",
                            json={
                                "access_token": test_db_with_user.get('access_token'),
                                "username": test_db_with_user.get('username')
                            })

    assert info_req.status_code == 200
    assert info_req.json()['username'] == 'test'
    assert info_req.json()['display_name'] == 'test'


def test_get_user_info_invalid_username(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    info_req = requests.get(f"{server_address}/api/v2/user/info",
                            json={
                                "access_token": test_db_with_user.get('access_token'),
                                "username": "missing_username"
                            })

    assert info_req.status_code == 404
    assert info_req.json()['error'] == ErrorCodes.USERNAME_NOT_FOUND.value


def test_get_user_info_missing_data(test_db_with_user, server_address, monkeypatch):
    monkeypatch.setattr("socialserver.api.v2.user.db", test_db_with_user.get('db'))
    monkeypatch.setattr("socialserver.util.auth.db", test_db_with_user.get('db'))

    info_req = requests.get(f"{server_address}/api/v2/user/info",
                            json={})

    assert info_req.status_code == 400


# TODO: pictures. api2 doesn't even have support for these yet, so it shouldn't be an issue
