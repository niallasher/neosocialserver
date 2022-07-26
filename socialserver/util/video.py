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
from pony.orm import commit, select
from socialserver.util.output import console
from tempfile import NamedTemporaryFile
from hashlib import sha256
from socialserver.util.filesystem import fs_videos


class InvalidVideoException(Exception):
    pass


def _verify_video(video: BytesIO):
    if not check_buffer_mimetype(video, VIDEO_SUPPORTED_FORMATS):
        raise InvalidVideoException


def write_video(video: BytesIO, video_hash: str) -> None:
    console.log(f"Writing new video, hash={video_hash}")
    # FIXME: testing needs work before this is removed.
    if fs_videos.exists(f"/{video_hash}"):
        return

    fs_videos.makedir(f"/{video_hash}")
    fs_videos.writebytes(f"/{video_hash}/video.mp4", video.read())


# screenshot the first frame of a video, so we can make thumbnails etc. out of it.
def screenshot_video(video: BytesIO) -> BytesIO:
    with NamedTemporaryFile() as input_file:
        # it's not nice to use a file on disk, but it has benefits here.
        # ^^ what did I mean by this?
        video.seek(0)
        input_file.write(video.read())
        # return cursor since we're sharing this buffer.
        video.seek(0)
        video_object = ffmpeg.input(input_file.name)
        try:
            output, _ = video_object.output("pipe:", format="image2", vframes="1").run(
                capture_stdout=True
            )
        except ffmpeg.Error:
            raise InvalidVideoException
    return BytesIO(output)


def handle_video_upload(video: BytesIO, userid: int) -> SimpleNamespace:
    _verify_video(video)
    identifier = token_urlsafe(32)

    # we already know the user exists,
    # since we're calling this from an authenticated API route!
    # (or at least we should be...)
    user = db.User.get(id=userid)

    video_hash = sha256(video.read()).hexdigest()
    video.seek(0)

    existing_video = select(
        video for video in db.Video if video.sha256sum is video_hash
    ).limit(1)[::]
    existing_video = existing_video[0] if len(existing_video) >= 1 else None

    # we're not reusing thumbnails directly; we want the thumbnail object
    # to be owned by the user who uploaded the video. an identical video will have
    # an identical screenshot anyway, so it will still be handled properly.
    console.log("Capturing thumbnail from video")
    thumbnail_image = screenshot_video(video)
    console.log("Generating image upload from thumbnail capture")
    # we're using the database ID since it's internal,
    # not the user facing identifier
    thumbnail_id = handle_image_upload(thumbnail_image, userid, threaded=False).id

    commit()

    if existing_video is None:
        write_video(video, video_hash)

    video_db = db.Video(
        owner=user,
        creation_time=datetime.utcnow(),
        identifier=identifier,
        sha256sum=video_hash,
        thumbnail=db.Image.get(id=thumbnail_id),
        # true since we're just direct playing right now
        processed=True,
    )

    # save again, so that we can get the id of the stored object
    commit()

    return SimpleNamespace(id=video_db.id, identifier=identifier)
