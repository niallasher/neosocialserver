#  Copyright (c) Niall Asher 2022
# TODO: Optional S3 implementation for storage directories. Will need config file updates too.

from socialserver.util.config import config
from socialserver.util.output import console
from fs.osfs import OSFS
from typing import Union
from fs_s3fs import S3FS
from os import getenv
import atexit


def _close_filesystem(fs: Union[OSFS, S3FS], title: str):
    console.log(f"Closing {title} filesystem object...")
    fs.close()


IMAGE_STORAGE_DIR_OVERRIDE = getenv("SOCIALSERVER_IMAGE_STORAGE_DIR", None)
VIDEO_STORAGE_DIR_OVERRIDE = getenv("SOCIALSERVER_VIDEO_STORAGE_DIR", None)

video_dir = VIDEO_STORAGE_DIR_OVERRIDE or config.media.videos.storage_dir
image_dir = IMAGE_STORAGE_DIR_OVERRIDE or config.media.images.storage_dir

fs_images = OSFS(image_dir, create=True)
fs_videos = OSFS(video_dir, create=True)

# close all filesystems safely during program exit.
atexit.register(lambda: _close_filesystem(fs_images, "image"))
atexit.register(lambda: _close_filesystem(fs_videos, "video"))
