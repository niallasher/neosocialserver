# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, convert_remote_image_to_data_url, create_image_package_from_data_url, \
    server_address
from socialserver.constants import ErrorCodes
import requests

image_data_url = convert_remote_image_to_data_url("https://picsum.photos/512.jpg")


def test_upload_image(test_db, server_address):
    r = requests.post(f"{server_address}/api/v3/image",
                      json={
                          'image_package': create_image_package_from_data_url(image_data_url)
                      },
                      headers={
                          "Authorization": f"Bearer {test_db.access_token}"
                      })
    print(r.json())
    assert r.status_code == 201


def test_get_image(test_db, server_address):
    image_identifier = requests.post(f"{server_address}/api/v3/image",
                                     json={
                                         'image_package': create_image_package_from_data_url(image_data_url)
                                     },
                                     headers={
                                         "Authorization": f"Bearer {test_db.access_token}"
                                     }).json()['identifier']
    r = requests.get(f"{server_address}/api/v3/image/{image_identifier}",
                     json={
                         "wanted_type": "post",
                         "pixel_ratio": 1
                     })
    assert r.status_code == 200


def test_get_image_invalid_use(test_db, server_address):
    image_identifier = requests.post(f"{server_address}/api/v3/image",
                                     json={
                                         'image_package': create_image_package_from_data_url(image_data_url)
                                     },
                                     headers={
                                         "Authorization": f"Bearer {test_db.access_token}"
                                     }).json()['identifier']
    r = requests.get(f"{server_address}/api/v3/image/{image_identifier}",
                     json={
                         "wanted_type": "invalid_post_type",
                         "pixel_ratio": 1
                     })
    assert r.status_code == 400
    assert r.json()['error'] == ErrorCodes.IMAGE_TYPE_INVALID.value


def test_get_image_invalid_identifier(test_db, server_address):
    r = requests.get(f"{server_address}/api/v3/image/abcxyz123",
                     json={
                         "wanted_type": "post",
                         "pixel_ratio": 1
                     })
    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.IMAGE_NOT_FOUND.value
