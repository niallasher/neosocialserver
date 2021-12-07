import datetime
from hashlib import sha256
import re
from base64 import b64decode
from io import BytesIO
from math import gcd
from os import makedirs, mkdir, path
from types import SimpleNamespace
import PIL
from PIL import Image, ImageOps
from pony.orm import commit, db_session
from socialserver.util.config import config
from socialserver.db import DbImage, DbUser
from socialserver.constants import ImageUploadTypes, ImageTypes,  MAX_PIXEL_RATIO, MAX_IMAGE_SIZE_GALLERY_PREVIEW, MAX_IMAGE_SIZE_POST_PREVIEW, MAX_IMAGE_SIZE_POST, MAX_IMAGE_SIZE_HEADER, MAX_IMAGE_SIZE_PROFILE_PICTURE, MAX_IMAGE_SIZE_PROFILE_PICTURE_LARGE
from secrets import token_urlsafe
from json import loads
from copy import copy
from rich import print


IMAGE_DIR = config.media.images.storage_dir
# where straight uploaded images are stored.
# the optimized ones are stored one above it
IMAGE_DIR_ORIGINAL = IMAGE_DIR + '/originals'
IMAGE_QUALITY = config.media.images.quality


# check if the image directory exists,
# if it doesn't, create it
if not path.exists(IMAGE_DIR):
    makedirs(IMAGE_DIR)
    print(f"Created image storage directory, {IMAGE_DIR}")


"""
    save_imageset_to_disk
    Saves an imageset (e.g. profile pic sm, lg) to disk, in the correct directory, with consistent naming.
    Does not create a database entry.
    in the future, this might be moved into amazon s3?
"""


# TODO: not sure how to dest represent a dict with pythons type
# annotations. Need to fix this.
def save_images_to_disk(images: dict(), access_id: str) -> None:

    def save_with_pixel_ratio(image, filename, pixel_ratio):
        image.save(f"{IMAGE_DIR}/{access_id}/{filename}_{pixel_ratio}x.jpg",
                   type="JPEG", quality=IMAGE_QUALITY)

    mkdir(f"{IMAGE_DIR}/{access_id}")
    print(images.keys())
    for i in images.keys():
        print(i.value)
        if i == ImageTypes.ORIGINAL:
            print("saving original image.")
            images[i][0].save(
                f"{IMAGE_DIR}/{access_id}/{ImageTypes.ORIGINAL.value}.jpg", type="JPEG", quality=IMAGE_QUALITY)
        else:
            for j in images[i]:
                save_with_pixel_ratio(j, i.value, images[i].index(j)+1)


"""
    create_random_image_identier
    return a random identifier to be associated with an image,
    for retrieval purposes
"""


def create_random_image_identifier() -> str:
    return token_urlsafe(32)


"""
    mult_size_tuple
    returns a new size tuple, multipled from the given
    one, for pixel ratio stuff
"""


def mult_size_tuple(size: tuple(int, int), multiplier: int) -> tuple(int, int):
    return (size[0]*multiplier, size[1]*multiplier)


"""
    fit_image_to_size
    Resizes an image to fit within the given size.
    Doesn't care about MAX_PIXEL_RATIO; it's just the
    unmodified original image.
"""


def fit_image_to_size(image: PIL.Image, size: tuple(int, int)) -> PIL.Image:
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


def resize_image_aspect_aware(image: PIL.Image, size: tuple(int, int)) -> PIL.Image:
    #  TODO: this really need to make sure the image isn't
    #  smaller than the requested size already, since we don't
    #  want to make the size LARGER!
    images = []
    if image.size[0] < size[0] or image.size[1] < size[1]:
        # create the largest possible image within max_image_size
        size = calculate_largest_fit(image, size)
        return
    for pixel_ratio in range(1, MAX_PIXEL_RATIO + 1):
        scaled_size = mult_size_tuple(size, pixel_ratio)
        # if the scaled size is larger than the original, use the original
        if scaled_size[0] > image.size[0] or scaled_size[1] > image.size[1]:
            scaled_size = size
        images.append(
            ImageOps.fit(
                image,
                scaled_size,
                PIL.Image.BICUBIC,
                centering=(0.5, 0.5)
            )
        )
    return images


"""
    calculate largest image size to fit in the aspect ratio
    given by a size.
    used to prevent resizing an image to be larger than
    it was originally, since that is pretty bad for optimization 
    (mind blowing, i know)
"""


def calculate_largest_fit(image: PIL.Image, max_size: tuple(int, int)) -> tuple(int, int):
    # calculate *target* aspect ratio from max size
    divisor = gcd(max_size[0], max_size[1])
    target_aspect_ratio = (max_size[0] / divisor, max_size[1] / divisor)
    # create the largest possible image within the original image size, and the aspect ratio
    new_width = image.size[0] - (image.size[0] % target_aspect_ratio[0])
    new_height = new_width * (target_aspect_ratio[0] / target_aspect_ratio[1])
    return (new_width, new_height)


"""
    convert_data_url_to_image
    Converts a data url to a PIL image, for further processing.
    Does not resize, compress or save the image. Just loads it,
    and returns it.
"""


def convert_data_url_to_image(data_url: str) -> PIL.Image:
    # strip the mime type declaration, and the data: prefix
    # so we can convert to binary and create an image
    data_url = re.sub(r'^data:image/.+;base64,', '', data_url)
    # we're storing in BytesIO so we don't have to
    # write to disk, and we can use the image directly.
    # we only want to store it once processing is done.
    binary_data = BytesIO(b64decode(data_url))
    image = Image.open(binary_data).convert('RGB')
    return image


"""
    commit_image_to_db
    Commit DbImage entry to the database, and then return it's id.
"""


@db_session
def commit_image_to_db(identifier: str, userid: int) -> None or int:
    uploader = DbUser.get(id=userid)
    if uploader == None:
        print("Could not commit to DB: user id does not exist!")
    else:
        entry = DbImage(
            creation_time=datetime.datetime.now(),
            identifier=identifier,
            uploader=DbUser.get(id=userid)
        )
        commit()
        return entry.id


"""
    handle_upload
    Take a JSON string (read notes.md, #images) containing b64 images, and process it.
    Will save it, store a db entry, and return
    a SimpleNamespace with the following keys:
        - id: DbImage ID
        - uid: Image identifier
"""


def handle_upload(image_package: dict(), upload_type_int: int, userid: int) -> None:
    # Retrieve enum value for upload type
    upload_type = ImageUploadTypes(upload_type_int)
    # deserialize the JSON containing image dataurls
    images = loads(image_package)
    # if the client didn't supply a cropped image for the purpose,
    # we'll just use the original image in it's place.
    # this is a fallback, in case of a client that doesn't do
    # due diligence.
    # tldr: unlike customer service, it's usually the client who is wrong.
    if ('cropped' not in images.keys()):
        image = convert_data_url_to_image(images['original'])
        original_image = copy(image)
    else:
        image = convert_data_url_to_image(images['cropped'])
        original_image = convert_data_url_to_image(images['original'])
    upload_type = ImageUploadTypes(upload_type_int)
    access_id = create_random_image_identifier()

    # all resized images get 4 different pixel ratios, returned in an array from
    # 0 to 3, where the pixel ratio is the index + 1. except for posts.
    # we always deliver them in ''full'' quality (defined by MAX_IMAGE_SIZE_POST)
    arr_gallery_preview_image = resize_image_aspect_aware(
        image, MAX_IMAGE_SIZE_GALLERY_PREVIEW)

    images = {
        ImageTypes.ORIGINAL: [original_image],
        ImageTypes.GALLERY_PREVIEW: arr_gallery_preview_image
    }

    if upload_type == ImageUploadTypes.PROFILE_PICTURE:
        arr_profilepic = resize_image_aspect_aware(
            image, MAX_IMAGE_SIZE_PROFILE_PICTURE)
        arr_profilepic_lg = resize_image_aspect_aware(
            image, MAX_IMAGE_SIZE_PROFILE_PICTURE_LARGE)
        images[ImageTypes.PROFILE_PICTURE] = arr_profilepic
        images[ImageTypes.PROFILE_PICTURE_LARGE] = arr_profilepic_lg

    if upload_type == ImageUploadTypes.POST:
        img_post = fit_image_to_size(
            image, MAX_IMAGE_SIZE_POST)
        arr_post_preview = resize_image_aspect_aware(
            image, MAX_IMAGE_SIZE_POST_PREVIEW)
        images[ImageTypes.POST] = [img_post]
        images[ImageTypes.POST_PREVIEW] = arr_post_preview

    if upload_type == ImageUploadTypes.HEADER:
        header = resize_image_aspect_aware(
            image, MAX_IMAGE_SIZE_HEADER)
        images[ImageTypes.HEADER] = [header]

    save_images_to_disk(images, access_id)
    entry = commit_image_to_db(access_id, userid)
    return SimpleNamespace(
        id=entry,
        identifier=access_id
    )
