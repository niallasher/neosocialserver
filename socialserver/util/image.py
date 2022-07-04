#  Copyright (c) Niall Asher 2022

import datetime
import re
from base64 import urlsafe_b64decode
from math import gcd
from types import SimpleNamespace
from base64 import b64encode
import PIL
from PIL import Image, ImageOps, ExifTags
from pony.orm import commit, db_session, select
from socialserver.util.config import config
from socialserver.util.output import console
from socialserver.db import db
from socialserver.util.filesystem import fs_images
from socialserver.constants import (
    ImageTypes,
    MAX_PIXEL_RATIO,
    MAX_IMAGE_SIZE_GALLERY_PREVIEW,
    MAX_IMAGE_SIZE_POST_PREVIEW,
    MAX_IMAGE_SIZE_POST,
    MAX_IMAGE_SIZE_PROFILE_PICTURE,
    MAX_IMAGE_SIZE_PROFILE_PICTURE_LARGE,
    ImageSupportedMimeTypes,
    BLURHASH_X_COMPONENTS,
    BLURHASH_Y_COMPONENTS,
    PROCESSING_BLURHASH,
)
from secrets import token_urlsafe
from copy import copy
import magic
from typing import Tuple
import blurhash
from io import BytesIO
from threading import Thread
from hashlib import sha256

IMAGE_QUALITY = config.media.images.quality
GENERATE_WEBP_IMAGES = config.media.images.generate_webp_images

"""
    rotate_image_accounting_for_exif_data
    Reads the Exif tags associated with an uploaded image.
    If it finds a rotation tag, it will apply the correct rotation to the image object.
    Important for iOS image uploads, which always seem to end up the wrong way around.
"""


def rotate_image_accounting_for_exif_data(image_object: Image) -> Image:
    # this may have issues with png depending on pillow version!
    # might need to be done manually.
    console.log("Rotating image to account for exif orientation data.")
    rotated_image = ImageOps.exif_transpose(image_object)
    return rotated_image


"""
    save_imageset_to_disk
    Saves an imageset (e.g. profile pic sm, lg) to disk, in the correct directory, with consistent naming.
    Does not create a database entry.
    in the future, this might be moved into amazon s3?
"""


# TODO: not sure how to best represent a dict with pythons type
# annotations. Need to fix this.
def save_images_to_disk(images: dict, image_hash: str, use_webp=False) -> None:
    image_format = "WEBP" if use_webp else "JPEG"
    image_ext = "webp" if use_webp else "jpg"

    def save_with_pixel_ratio(image, filename, pixel_ratio):

        print(f"\n\n\n processing image pr {pixel_ratio} \n\n\n")

        # this isn't that efficient, but I'm not aware of a better way
        # without using syspath.
        # using the fs object is more secure, since it can't affect anything
        # above its root directory, limiting what could happen with paths

        temp_image_buffer = BytesIO()
        # we save to the temporary image buffer since we're
        # using pyfilesystem now, and we don't want this step
        # to depend on any specific backend.
        image.save(
            temp_image_buffer,
            format=image_format,
            quality=IMAGE_QUALITY,
            progressive=True,
        )
        temp_image_buffer.seek(0)
        # in the future this may be abstracted further.
        fs_images.writebytes(
            f"/{image_hash}/{filename}_{pixel_ratio}x.{image_ext}", temp_image_buffer.read()
        )
        del temp_image_buffer

    # FIXME: this is due to some deficiencies in the testing process.

    print("\n\n\n\n\n\n")
    if not fs_images.exists(f"/{image_hash}"):
        console.log(f"Creating images/{image_hash}...")
        fs_images.makedir(f"/{image_hash}")
    print("\n\n\n\n\n\n")

    for i in images.keys():
        if i == ImageTypes.ORIGINAL:
            console.log(f"Saving original image ({image_ext}) for {image_hash}")
            temp_image_buffer = BytesIO()
            images[i][0].save(
                temp_image_buffer,
                format=image_format,
                quality=IMAGE_QUALITY,
            )
            temp_image_buffer.seek(0)
            fs_images.writebytes(
                f"/{image_hash}/{ImageTypes.ORIGINAL.value}.{image_ext}", temp_image_buffer.read()
            )
            del temp_image_buffer
        else:
            counter = 1
            for j in images[i]:
                console.log(f"Saving {i.value }image ({image_ext}) for {image_hash}")
                save_with_pixel_ratio(j, i.value, counter)
                counter += 1
                # FIXME: incredibly hacky way of dealing with duplicates.
                # images[i][images[i].index(j)] = token_urlsafe(16)


"""
    create_random_image_identifier
    return a random identifier to be associated with an image,
    for retrieval purposes
"""


def create_random_image_identifier() -> str:
    return token_urlsafe(32)


"""
    mult_size_tuple
    returns a new size tuple, multiplied from the given
    one, for pixel ratio stuff
"""


def mult_size_tuple(size: Tuple[int, int], multiplier: int) -> Tuple[int, int]:
    return tuple((int(size[0] * multiplier), int(size[1] * multiplier)))


"""
    fit_image_to_size
    Resizes an image to fit within the given size.
    Doesn't care about MAX_PIXEL_RATIO; it's just the
    unmodified original image.
"""


def fit_image_to_size(image: PIL.Image, size: Tuple[int, int]) -> PIL.Image:
    img = copy(image)
    img.thumbnail(size, PIL.Image.ANTIALIAS)
    return img


"""
    resize_image_aspect_aware
    Resize an image, aspect aware.
    Returns the result of fit_image_to_size after cropping to aspect
    ratio from the top left. (i.e. you will get back an array of images,
    for different pixel ratios, from 1 to MAX_PIXEL_RATIO)
"""


# TODO: fix typing returns a list of images
def resize_image_aspect_aware(image: PIL.Image, size: Tuple[int, int]) -> PIL.Image:
    #  TODO: this really need to make sure the image isn't
    #  smaller than the requested size already, since we don't
    #  want to make the size LARGER!
    images = []
    if image.size[0] < size[0] or image.size[1] < size[1]:
        # create the largest possible image within max_image_size
        size = calculate_largest_fit(image, size)
    for pixel_ratio in range(1, MAX_PIXEL_RATIO + 1):
        scaled_size = mult_size_tuple(size, pixel_ratio)
        # if the scaled size is larger than the original, use the original
        if scaled_size[0] > image.size[0] or scaled_size[1] > image.size[1]:
            # TODO: see why the hell these are coming out as floats...
            scaled_size = (int(size[0]), int(size[1]))
        images.append(
            ImageOps.fit(image, scaled_size, PIL.Image.BICUBIC, centering=(0.5, 0.5))
        )
    return images


"""
    calculate largest image size to fit in the aspect ratio
    given by a size.
    used to prevent resizing an image to be larger than
    it was originally, since that is pretty bad for optimization
    (mind blowing, i know)
"""


def calculate_largest_fit(
        image: PIL.Image, max_size: Tuple[int, int]
) -> Tuple[int, int]:
    # calculate *target* aspect ratio from max size
    divisor = gcd(max_size[0], max_size[1])
    target_aspect_ratio = (max_size[0] / divisor, max_size[1] / divisor)
    # create the largest possible image within the original image size, and the aspect ratio
    new_width = image.size[0] - (image.size[0] % target_aspect_ratio[0])
    new_height = new_width * (target_aspect_ratio[0] / target_aspect_ratio[1])
    return tuple((new_width, new_height))


"""
    convert_data_url_to_byte_buffer
    Converts a data url to a BytesIO buffer, for further processing.
    Does not resize, compress or save the image. Just loads it,
    and returns it.
"""


def convert_data_url_to_byte_buffer(data_url: str) -> BytesIO:
    # strip the mime type declaration, and the data: prefix,
    # so we can convert to binary and create an image
    data_url = re.sub(r"^data:image/.+;base64,", "", data_url)
    # we're storing in BytesIO, so we don't have to
    # write to disk, and we can use the image directly.
    # we only want to store it once processing is done.
    binary_data = BytesIO(urlsafe_b64decode(data_url))
    return binary_data


""" 
    convert_buffer_to_image
    
    Converts a buffer to a pil.Image object
"""


def convert_buffer_to_image(buffer: BytesIO) -> PIL.Image:
    image = Image.open(buffer).convert("RGB")
    return image


"""
    commit_image_to_db
    Commit db.Image entry to the database, and then return it's id.
"""


@db_session
def commit_image_to_db(identifier: str, userid: int, blur_hash: str) -> None or int:
    uploader = db.User.get(id=userid)
    if uploader is None:
        console.log("[bold red]Could not commit to DB: user id does not exist!")
    else:
        entry = db.Image(
            creation_time=datetime.datetime.utcnow(),
            identifier=identifier,
            uploader=db.User.get(id=userid),
            blur_hash=blur_hash,
        )
        commit()
        return entry.id


"""
    generate_image_of_type
    Optimize the original copy of an already uploaded image
    for a new type. Raises an exception if the image cannot be converted.
"""


def generate_image_of_type(identifier):
    image_exists = db.Image.get(identifier=identifier) is not None
    if not image_exists:
        raise Exception("image not found")
    pass


"""
    InvalidImageException
    
    Raised if there is an issue with the image format
"""


class InvalidImageException(Exception):
    pass


"""
    check_buffer_mimetype
    
    Check the file type of binary data, to ensure it matches an
    array of mimetypes. Returns true if ok, false if not.
"""


# TODO: if we're using this in multiple places it should be moved to socialserver.util.file!
def check_buffer_mimetype(buffer, mimetypes):
    mimetype = magic.from_buffer(buffer.read(2048), mime=True)
    buffer.seek(0)
    if mimetype not in mimetypes:
        return False
    return True


"""
    _verify_image
        
    verify an image using libmagic
"""


def _verify_image(image: BytesIO):
    if not check_buffer_mimetype(image, ImageSupportedMimeTypes):
        raise InvalidImageException

    # we don't need to return anything;
    # the exception will interrupt control
    # flow if we have a problem. Otherwise,
    # we just want to continue


"""
    check_image_exists
    check if an image exists based on it's id
"""


def check_image_exists(identifier: str):
    return db.Image.get(identifier=identifier) is not None


"""
    get_image_data_url_legacy
    
    gets an image as a dataurl, for use with the legacy client.
"""


def get_image_data_url_legacy(identifier: str, image_type: ImageTypes) -> str:
    image = db.Image.get(identifier=identifier)
    if image is None:
        raise InvalidImageException

    pixel_ratio = config.legacy_api_interface.image_pixel_ratio
    if image_type == ImageTypes.POST.value:
        # only 1x for posts, since we store them at a very high size already.
        # no other pixel ratio variants exist!
        pixel_ratio = 1

    file = f"/{image.sha256sum}/{image_type.value}_{pixel_ratio}x.jpg"
    if not fs_images.exists(file):
        raise InvalidImageException

    file_data = fs_images.readbytes(file)

    return "data:image/jpg;base64," + b64encode(file_data).decode()


"""
    generate_blur_hash
    Generate a blur hash from a given image
"""


def generate_blur_hash(image: Image) -> str:
    im = copy(image)
    buffer = BytesIO()
    im.save(buffer, format="jpeg")
    blur_hash = blurhash.encode(buffer, BLURHASH_X_COMPONENTS, BLURHASH_Y_COMPONENTS)
    return blur_hash


"""
    process_image
    Convert the image into the appropriate format and commit it to the disk.
"""


@db_session
def process_image(image: Image, image_hash: str, image_id: int) -> None:
    console.log(f"Processing image, id={image_id}. sha256sum={image_hash}")
    # all resized images get 4 different pixel ratios, returned in an array from
    # 0 to 3, where the pixel ratio is the index + 1. except for posts.
    # we always deliver them in ''full'' quality (defined by MAX_IMAGE_SIZE_POST)
    arr_gallery_preview_image = resize_image_aspect_aware(
        image, MAX_IMAGE_SIZE_GALLERY_PREVIEW
    )

    # if upload_type == ImageUploadTypes.PROFILE_PICTURE:
    arr_profilepic = resize_image_aspect_aware(image, MAX_IMAGE_SIZE_PROFILE_PICTURE)
    arr_profilepic_lg = resize_image_aspect_aware(
        image, MAX_IMAGE_SIZE_PROFILE_PICTURE_LARGE
    )
    img_post = fit_image_to_size(image, MAX_IMAGE_SIZE_POST)
    arr_post_preview = resize_image_aspect_aware(image, MAX_IMAGE_SIZE_POST_PREVIEW)

    arr_header = resize_image_aspect_aware(image, MAX_IMAGE_SIZE_POST)

    images = {
        ImageTypes.ORIGINAL: [image],
        ImageTypes.POST: [img_post],
        ImageTypes.POST_PREVIEW: arr_post_preview,
        ImageTypes.HEADER: arr_header,
        ImageTypes.GALLERY_PREVIEW: arr_gallery_preview_image,
        ImageTypes.PROFILE_PICTURE: arr_profilepic,
        ImageTypes.PROFILE_PICTURE_LARGE: arr_profilepic_lg,
    }

    save_images_to_disk(images, image_hash)
    if GENERATE_WEBP_IMAGES:
        console.log(f"Generating WEBP images for image {image_id}...")
        save_images_to_disk(images, image_hash, use_webp=True)

    db_image = db.Image.get(id=image_id)
    db_image.processed = True
    db_image.blur_hash = generate_blur_hash(image)

    commit()

    console.log(f"Image, id={image_id}, processed.")


"""
    handle_upload
    Take a JSON string (read notes.md, #images) containing b64 images, and process it.
    Will save it, store a db entry, and return
    a SimpleNamespace with the following keys:
        - id: db.Image ID
        - uid: Image identifier
"""


@db_session
def handle_upload(
        image: BytesIO, userid: int, threaded: bool = True
) -> SimpleNamespace:
    # check that the given data is valid.
    _verify_image(image)

    uploader = db.User.get(id=userid)
    if uploader is None:
        console.log("[bold red]Could not commit to DB: user id does not exist!")
        raise InvalidImageException  # should maybe rename this?

    # before we bother processing the image, we check if any image with an identical
    # hash exists, since there is no point duplicating them in storage.

    # get the hash of the image
    image_hash = sha256(image.read()).hexdigest()
    image.seek(0)

    # and try to find an existing Image with the same one.
    # if this != null, we'll use it to fill in some Image entry fields later.
    existing_image = select(
        image for image in db.Image if image.sha256sum is image_hash
    ).limit(1)[::]
    existing_image = existing_image[0] if len(existing_image) >= 1 else None

    image = convert_buffer_to_image(image)

    image = rotate_image_accounting_for_exif_data(image)

    access_id = create_random_image_identifier()

    # create the image entry now, so we can give back an identifier.
    entry = db.Image(
        creation_time=datetime.datetime.utcnow(),
        identifier=access_id,
        uploader=db.User.get(id=userid),
        blur_hash=PROCESSING_BLURHASH,
        sha256sum=image_hash,
        processed=False,
    )

    commit()

    if existing_image is not None:
        entry.blur_hash = existing_image.blur_hash
        entry.processed = True
        return SimpleNamespace(id=entry.id, identifier=access_id, processed=True)

    if threaded:
        Thread(target=lambda: process_image(image, image_hash, entry.id)).start()
    else:
        process_image(image, image_hash, entry.id)

    # if we're not using threading, then it will have been processed by now.
    return SimpleNamespace(id=entry.id, identifier=access_id, processed=(not threaded))
