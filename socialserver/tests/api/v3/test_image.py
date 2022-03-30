#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, image_data_binary
from socialserver.constants import ErrorCodes, ImageTypes
import requests


def test_upload_image(test_db, server_address, image_data_binary):
    r = requests.post(
        f"{server_address}/api/v3/image/process_before_return",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    print(r.text)
    assert r.status_code == 201


def test_get_image(test_db, server_address, image_data_binary):
    image_identifier = requests.post(
        f"{server_address}/api/v3/image/process_before_return",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    ).json()["identifier"]
    print(image_identifier)
    r = requests.get(
        f"{server_address}/api/v3/image/{image_identifier}",
        json={"wanted_type": "post", "pixel_ratio": 1},
    )
    assert r.status_code == 200


def test_get_image_invalid_use(test_db, server_address, image_data_binary):
    image_identifier = requests.post(
        f"{server_address}/api/v3/image/process_before_return",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    ).json()["identifier"]
    r = requests.get(
        f"{server_address}/api/v3/image/{image_identifier}",
        json={"wanted_type": "invalid_post_type", "pixel_ratio": 1},
    )
    assert r.status_code == 400
    assert r.json()["error"] == ErrorCodes.IMAGE_TYPE_INVALID.value


def test_get_image_invalid_identifier(test_db, server_address, image_data_binary):
    r = requests.get(
        f"{server_address}/api/v3/image/abcxyz123",
        json={"wanted_type": "post", "pixel_ratio": 1},
    )
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.IMAGE_NOT_FOUND.value


def test_upload_image_threaded(test_db, server_address, image_data_binary):
    r = requests.post(
        f"{server_address}/api/v3/image",
        files={"image": image_data_binary},
        headers={"Authorization": f"Bearer {test_db.access_token}"},
    )
    print(r.json())
    assert r.status_code == 201
    assert r.json()["processed"] is False
    identifier = r.json()["identifier"]
    r = requests.get(
        f"{server_address}/api/v3/image/{identifier}",
        json={"wanted_type": ImageTypes.POST.value, "pixel_ratio": 1},
    )
    assert r.status_code == 404
    assert r.json()["error"] == ErrorCodes.IMAGE_NOT_PROCESSED.value
