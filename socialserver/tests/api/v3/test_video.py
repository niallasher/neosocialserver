#  Copyright (c) Niall Asher 2022

# noinspection PyUnresolvedReferences
from socialserver.util.test import test_db, server_address, image_data_binary, video_data_binary
from socialserver.constants import ErrorCodes
import requests


def test_upload_video(test_db, server_address, video_data_binary):
    r = requests.post(f"{server_address}/api/v3/videos",
                      files={
                          "video": video_data_binary
                      },
                      headers={
                          "Authorization": f"Bearer {test_db.access_token}"
                      })
    assert r.status_code == 201


def test_get_video(test_db, server_address, video_data_binary):
    video_identifier = requests.post(f"{server_address}/api/v3/videos",
                                     files={
                                         "video": video_data_binary
                                     },
                                     headers={
                                         "Authorization": f"Bearer {test_db.access_token}"
                                     }).json()['identifier']
    print(video_identifier)
    r = requests.get(f"{server_address}/api/v3/videos/{video_identifier}")
    print(r.tet)
    assert r.status_code == 200


def test_get_video_invalid_identifier(test_db, server_address, image_data_binary):
    r = requests.get(f"{server_address}/api/v3/videos/doesnt_exist")
    assert r.status_code == 404
    assert r.json()['error'] == ErrorCodes.OBJECT_NOT_FOUND.value
