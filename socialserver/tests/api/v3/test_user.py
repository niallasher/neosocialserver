#  Copyright (c) Niall Asher 2022

# pycharm isn't detecting fixture usage, so we're
# disabling PyUnresolvedReferences for the import.
# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, image_data_binary
import requests
from pony.orm import db_session
from socialserver.constants import (
    ErrorCodes,
    BIO_MAX_LEN,
    DISPLAY_NAME_MAX_LEN,
    MAX_PASSWORD_LEN,
)
from secrets import token_urlsafe


def test_create_user(test_db, server_address):
    user_creation_request = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": "password",
        },
    )
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_with_bio(test_db, server_address):
    user_creation_request = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": "password",
            "bio": "something goes here",
        },
    )
    assert user_creation_request.status_code.__int__() == 201


def test_create_user_bio_too_long(test_db, server_address):
    user_creation_request = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": "password",
            "bio": token_urlsafe(BIO_MAX_LEN + 1),
        },
    )
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()["error"] == ErrorCodes.BIO_NON_CONFORMING.value


@db_session
def test_attempt_create_duplicate_user(test_db, server_address):
    requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": "password",
        },
    )
    user_creation_request = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": "password",
        },
    )
    print(user_creation_request.json())
    assert user_creation_request.status_code.__int__() == 400
    assert user_creation_request.json()["error"] == ErrorCodes.USERNAME_TAKEN.value


def test_create_user_missing_args(test_db, server_address):
    assert requests.post(f"{server_address}/api/v3/user", json={}).status_code == 400


def test_create_user_username_too_long(test_db, server_address):
    invalid_req = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "idontknowwhattoputherebutitsgottabelong",
            "password": "password",
        },
    )
    assert invalid_req.status_code == 400
    assert invalid_req.json()["error"] == ErrorCodes.USERNAME_INVALID.value


def test_create_user_password_too_short(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v3/user",
        json={"display_name": "Test User", "username": "testuser", "password": "a"},
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.PASSWORD_NON_CONFORMING.value


def test_create_user_password_too_long(test_db, server_address):
    r = requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User",
            "username": "testuser",
            "password": token_urlsafe(MAX_PASSWORD_LEN + 1),
        },
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.PASSWORD_NON_CONFORMING.value


def test_delete_user(test_db, server_address):
    del_req = requests.delete(
        f"{server_address}/api/v3/user",
        json={"password": test_db.password},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(del_req.json())
    assert del_req.status_code == 200


@db_session
def test_delete_user_invalid_password(test_db, server_address):
    del_req = requests.delete(
        f"{server_address}/api/v3/user",
        json={"password": "defo_not_the_right_password"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(del_req.json())
    assert del_req.status_code == 401
    assert del_req.json()["error"] == ErrorCodes.INCORRECT_PASSWORD.value


def test_delete_user_missing_input(test_db, server_address):
    del_req = requests.delete(
        f"{server_address}/api/v3/user",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert del_req.status_code == 400


def test_delete_user_invalid_token(test_db, server_address):
    del_req = requests.delete(
        f"{server_address}/api/v3/user",
        json={"password": test_db.password},
        headers={"Authorization": f"Bearer invalid"},
    )

    print(del_req.json())
    assert del_req.status_code == 401
    assert del_req.json()["error"] == ErrorCodes.TOKEN_INVALID.value


def test_update_username(test_db, server_address):
    del_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"username": "validusername"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(del_req.json())
    assert del_req.status_code == 200
    assert del_req.json()["username"] == "validusername"


def test_update_username_invalid(test_db, server_address):
    del_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"username": "defonotavalidusernamecuzitswaytoolong"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(del_req.json())
    assert del_req.status_code == 400
    assert del_req.json()["error"] == ErrorCodes.USERNAME_INVALID.value


def test_update_username_already_exists(test_db, server_address):
    # create a second user, so we can try to steal its name
    requests.post(
        f"{server_address}/api/v3/user",
        json={
            "display_name": "Test User 2",
            "username": "test2",
            "password": "password",
        },
    )

    del_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"username": "test2"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    print(del_req.json())
    assert del_req.status_code == 400
    assert del_req.json()["error"] == ErrorCodes.USERNAME_TAKEN.value


def test_update_bio(test_db, server_address):
    bio_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"bio": "this is the new bio content 😀"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert bio_req.status_code == 201


def test_update_bio_too_long(test_db, server_address):
    bio_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"bio": token_urlsafe(BIO_MAX_LEN + 1)},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert bio_req.status_code == 400
    assert bio_req.json()["error"] == ErrorCodes.BIO_NON_CONFORMING.value


def test_update_display_name(test_db, server_address):
    bio_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"display_name": "new name"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert bio_req.status_code == 201
    assert bio_req.json()["display_name"] == "new name"


def test_update_display_name_too_long(test_db, server_address):
    bio_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={"display_name": token_urlsafe(DISPLAY_NAME_MAX_LEN + 1)},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert bio_req.status_code == 400
    assert bio_req.json()["error"] == ErrorCodes.DISPLAY_NAME_NON_CONFORMING.value


def test_update_no_mod_params(test_db, server_address):
    bio_req = requests.patch(
        f"{server_address}/api/v3/user",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert bio_req.status_code == 400
    assert (
        bio_req.json()["error"] == ErrorCodes.USER_MODIFICATION_NO_OPTIONS_GIVEN.value
    )


def test_get_user_info(test_db, server_address):
    info_req = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": test_db.username},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert info_req.status_code == 200
    assert info_req.json()["username"] == "test"
    assert info_req.json()["display_name"] == "test"


def test_get_user_info_invalid_username(test_db, server_address):
    info_req = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": "missing_username"},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert info_req.status_code == 404
    assert info_req.json()["error"] == ErrorCodes.USERNAME_NOT_FOUND.value


def test_get_user_info_missing_data(test_db, server_address):
    info_req = requests.get(
        f"{server_address}/api/v3/user/info",
        json={},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )

    assert info_req.status_code == 400


def test_update_profile_pic(test_db, server_address, image_data_binary):
    # upload a new image
    image_identifier = requests.post(
        f"{server_address}/api/v3/image/process_before_return",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    ).json()["identifier"]
    r = requests.patch(
        f"{server_address}/api/v3/user",
        json={"profile_pic_ref": image_identifier},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 201
    # make sure the PFP from user info matches
    r = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": test_db.username},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 200
    assert r.json()["profile_picture"]["identifier"] == image_identifier


def test_update_profile_pic_invalid_ref(test_db, server_address, image_data_binary):
    image_identifier = "some_random_garbage_here_129839102"
    r = requests.patch(
        f"{server_address}/api/v3/user/process_before_return",
        json={"profile_pic_ref": image_identifier},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.IMAGE_NOT_FOUND.value
    # make sure the PFP from user info isn't our identifier
    # (intentionally not checking whether its None, since I'm
    # planning on a default PFP/header system soon!)
    r = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": test_db.username},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 200
    assert r.json()["profile_picture"]["identifier"] != image_identifier


def test_update_header_pic(test_db, server_address, image_data_binary):
    # upload a new image
    image_identifier = requests.post(
        f"{server_address}/api/v3/image/process_before_return",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    ).json()["identifier"]
    r = requests.patch(
        f"{server_address}/api/v3/user",
        json={"header_pic_ref": image_identifier},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 201
    # make sure the PFP from user info matches
    r = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": test_db.username},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 200
    assert r.json()["header"]["identifier"] == image_identifier


def test_update_header_pic_invalid_ref(test_db, server_address, image_data_binary):
    image_identifier = "some_random_garbage_here_129839102"
    r = requests.patch(
        f"{server_address}/api/v3/user",
        json={"header_pic_ref": image_identifier},
        headers={"Authorization": f"bearer {test_db.access_token}"},
    )
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.IMAGE_NOT_FOUND.value
    # make sure the PFP from user info isn't our identifier.
    r = requests.get(
        f"{server_address}/api/v3/user/info",
        json={"username": test_db.username},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    assert r.status_code == 200
    assert r.json()["header"]["identifier"] != image_identifier
