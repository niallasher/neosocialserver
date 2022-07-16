#  Copyright (c) Niall Asher 2022
from base64 import b64encode
from io import BytesIO
from PIL import Image
from socialserver.constants import ImageTypes, ROOT_DIR
from socialserver.util.config import config
from socialserver.util.filesystem import fs_images


def _load_thumbnail(thumbnail_sha256sum, format_ext: str) -> Image:
    thumbnail_bytes = BytesIO(
        fs_images.readbytes(f"/{thumbnail_sha256sum}" +
                            f"/{ImageTypes.POST_PREVIEW.value}" +
                            f"_{config.legacy_api_interface.image_pixel_ratio}x.{format_ext}")
    )

    return Image.open(thumbnail_bytes)


def make_unsupported_msg_thumbnail_b64(thumbnail_sha256sum) -> str:
    thumbnail = _load_thumbnail(thumbnail_sha256sum, "jpg")

    # we want the overlay to be of consistent size.
    # we can safely assume its aspect ratio is 1:1 because
    # it's cropped as such when generated.
    if thumbnail.width < 512 or thumbnail.width > 512:
        thumbnail = thumbnail.resize((512, 512))

    overlay = Image.open(
        f"{ROOT_DIR}/resources/legacy/video_unsupported_overlay.png"
    )

    # if we're serving webp images to legacy clients,
    # we're going to want to generate a webp here.
    output_format = "webp" if config.legacy_api_interface.send_webp_images else "JPEG"

    thumbnail.paste(overlay, (0, 0), overlay)
    output_buffer = BytesIO()
    thumbnail.save(output_buffer, format=output_format)

    output_buffer.seek(0)

    # TODO: all legacy data urls should have webp mimetype if the legacy send_webp_images
    # option is enabled!
    return "data:image/jpg;base64," + b64encode(output_buffer.read()).decode()
