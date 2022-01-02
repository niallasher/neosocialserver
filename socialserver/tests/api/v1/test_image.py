from socialserver.util.test import test_db, server_address, convert_remote_image_to_data_url
import requests

image_data_url = convert_remote_image_to_data_url("https://picsum.photos/512.jpg")


def test_upload_image_legacy(test_db, server_address):
    r = requests.post(f"{server_address}/api/v1/images",
                      json={
                          "session_token": test_db.access_token,
                          "image_data": image_data_url
                      })
    print(r.text)
    assert r.status_code == 201

# TODO: test with invalid images
