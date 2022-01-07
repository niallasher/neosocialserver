import argparse
import magic
import requests
from os import path
from base64 import urlsafe_b64encode

DEFAULT_SERVER_ADDR = "http://localhost:12345"
VALID_MIME_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/bmp"]

# this flag var will prevent any further action
# except session deletion if the upload fails
ok = True

parser = argparse.ArgumentParser(description="Handle things and stuff...")

parser.add_argument('path', type=str, help="Path to image that should be uploaded")
parser.add_argument('username', type=str, help="Username to authenticate with")
parser.add_argument('password', type=str, help="Password to authenticate with")
# TODO: totp once it's in the main server
parser.add_argument('--addr', type=str, help=f"Server address, defaults to {DEFAULT_SERVER_ADDR}",
                    default=DEFAULT_SERVER_ADDR)

args = parser.parse_args()

if not path.exists(args.path) or path.isdir(args.path):
    print("Path doesn't exist or is a directory!")
    exit(1)

try:
    # read in binary mode, since we're trying to read image data
    with open(args.path, "rb") as file:
        # we're only reading the first 2048 bytes,
        # for mimetype id purposes, so that we don't
        # load a giant file for no reason (if it isn't an image)
        initial_data = file.read(2048)
        mimetype = magic.from_buffer(initial_data, mime=True)
        if not mimetype in VALID_MIME_TYPES:
            print(f"Invalid mime type on file! Got {mimetype}, expected one of {VALID_MIME_TYPES}")
            exit(1)
        # we could seek and reuse this read, but there isn't much point. 
        # opening a second file handle isn't exactly going to hurt the
        # test perf of a rarely used test script :)
        # not that the server itself is particularly optimised right now anyway :))
except OSError:
    print("An exception occurred when reading the file, and determining it's mimetype!")
    exit(1)

# login to account
print("Getting access token")
login_req = requests.post(f'{args.addr}/api/v3/user/session',
                          json={
                              "username": args.username,
                              "password": args.password
                          }
                          )

if login_req.status_code == 401:
    print("Failed to log in!")
    exit(1)

access_token = login_req.json()['access_token']

# read the image and convert it to a dataurl
with open(args.path, "rb") as file:
    # urlsafe_b64encode returns bytes, so we decode it here aswell.
    image_data_url = f"data:{mimetype};base64," + urlsafe_b64encode(file.read()).decode()

print("Uploading image to server")
image_request = requests.post(f"{args.addr}/api/v3/image",
                              json={
                                  "original_image": image_data_url
                              },
                              headers={
                                  "Authorization": f"Bearer {access_token}"
                              })

if image_request.status_code != 201:
    ok = False
    print()
    print("Upload failed!")
    print(f"Request status code: {image_request.status_code}")
    print(f"Request error code: {image_request.json()['error']}")

# sign out
print("Revoking access token")
r = requests.delete(f"{args.addr}/api/v3/user/session",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    })

if not ok:
    exit(1)

print()
print("Uploaded!")
print(f"Image identifier: {image_request.json()['identifier']}")
