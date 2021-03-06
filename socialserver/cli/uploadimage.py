#  Copyright (c) Niall Asher 2022

from os import path
from json import dumps
from base64 import urlsafe_b64encode
import magic
from pony.orm import db_session
from io import BytesIO
from socialserver.constants import ImageSupportedMimeTypes
from socialserver.util.image import handle_upload


def image_to_b64(bio_obj, mimetype):
    data = urlsafe_b64encode(bio_obj.read()).decode()
    return f"data:{mimetype};base64,{data}"


@db_session
def upload_image(image_path):
    if not path.exists(image_path):
        print("Path not found!")
        return 1
    bio = BytesIO()
    with open(image_path, "rb") as image_binary:
        bio.write(image_binary.read())
        bio.seek(0)
    mimetype = magic.from_buffer(open(image_path, "rb").read(2048), mime=True)

    print(f"Image has mimetype: {mimetype}")
    if mimetype not in ImageSupportedMimeTypes:
        print("Image format not supported.")
        print("Refer to ImageSupportedMimetypes in socialserver.constants!")
        return 1

    image_b64 = image_to_b64(bio, mimetype)

    # FIXME: shouldn't be using hardcoded UID 1 here, it's just
    # for testing
    print(handle_upload(dumps({"original": image_b64}), 1))
