#  Copyright (c) Niall Asher 2022

import ffmpeg
from datetime import datetime
from secrets import token_urlsafe
from socialserver.util.image import check_buffer_mimetype
from socialserver.util.image import handle_upload as handle_image_upload
from types import SimpleNamespace
from io import BytesIO
from socialserver.constants import VIDEO_SUPPORTED_FORMATS
from socialserver.db import db
from pony.orm import commit
from socialserver.util.config import config
from socialserver.util.output import console
from os import makedirs, path, mkdir
from tempfile import NamedTemporaryFile

VIDEO_DIR = config.media.videos.storage_dir

if not path.exists(VIDEO_DIR):
    makedirs(VIDEO_DIR)
    console.log(f"Created image storage directory, {VIDEO_DIR}")


class InvalidVideoException(Exception):
    pass


def _verify_video(video: BytesIO):
    if not check_buffer_mimetype(video, VIDEO_SUPPORTED_FORMATS):
        raise InvalidVideoException


def write_video(video: BytesIO, access_id: str) -> None:
    mkdir(f"{VIDEO_DIR}/{access_id}")
    with open(f"{VIDEO_DIR}/{access_id}/video.mp4", "wb") as video_file:
        video_file.write(video.read())


# screenshot the first frame of a video, so we can make thumbnails etc. out of it.
def screenshot_video(video: BytesIO) -> BytesIO:
    with NamedTemporaryFile() as input_file:
        # it's not nice to use a file on disk, but it has benefits here.
        video.seek(0)
        input_file.write(video.read())
        video_object = ffmpeg.input(input_file.name)
        try:
            output, _ = video_object.output("pipe:", format="image2", vframes="1").run(
                capture_stdout=True
            )
        except ffmpeg.Error as e:
            raise InvalidVideoException
    return BytesIO(output)


def handle_video_upload(video: BytesIO, userid: int) -> SimpleNamespace:
    _verify_video(video)
    identifier = token_urlsafe(32)

    # we already know the user exists,
    # since we're calling this from an authenticated API route!
    user = db.User.get(id=userid)
    write_video(video, identifier)

    console.log("Capturing thumbnail from video")
    thumbnail_image = screenshot_video(video)
    console.log("Generating image upload from thumbnail capture")
    # we're using the database ID since it's internal,
    # not the user facing identifier
    thumbnail_id = handle_image_upload(thumbnail_image, userid, threaded=False).id

    # thumbnail_db = db.Image()

    # save the thumbnail, so we can reference it in the video db entry.
    commit()

    video_db = db.Video(
        owner=user,
        creation_time=datetime.now(),
        identifier=identifier,
        thumbnail=db.Image.get(id=thumbnail_id),
        # true since we're just direct playing right now
        processed=True,
    )

    # save again, so that we can
    commit()

    return SimpleNamespace(id=video_db.id, identifier=identifier)
