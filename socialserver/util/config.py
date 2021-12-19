import os
import toml
from attrdict import AttrDict
from rich.console import Console
from rich.traceback import install as install_traceback_handler
from pathlib import Path

# TODO: this should be in __init__.py once this module is actually a thing that's used by the rest of the code
install_traceback_handler()
console = Console()

HOME = os.getenv("HOME")

FILE_ROOT = os.getenv("SOCIALSERVER_ROOT", default=f"{HOME}/socialserver")

if FILE_ROOT is f"{HOME}/socialserver":
    console.log("The SOCIALSERVER_ROOT environment variable is unset! Please set it in your environment.")
    exit(1)

if not os.path.exists(FILE_ROOT):
    console.log("The SOCIALSERVER_ROOT folder, {FILE_ROOT} does not exist. Attempting to create it.")
    folder_path = Path(FILE_ROOT)
    folder_path.mkdir(parents=True)

DEFAULT_CONFIG_PATH = f"{FILE_ROOT}/config.toml"

CONFIG_PATH = os.getenv("SOCIALSERVER_CONFIG_FILE", default=DEFAULT_CONFIG_PATH)

DEFAULT_CONFIG = f"""
[network]
host = "0.0.0.0"
port = 51672

[database]
# supported connectors right now:
# sqlite, postgres
connector = "sqlite"
address = "{FILE_ROOT}/socialserver.db"


[media.images]
# this quality will be applied to 
# all non post images, except the saved
# original copy.
quality = 80
post_quality = 90
storage_dir = './media/images'

[auth.registration]
enabled = true
# if enabled, any admins will be
# able to get a list of requested
# signups, and approve or deny them
# before they are allowed in
approval_required = false

[posts]
# this is an anti-spam tactic; socialserver
# allows for each user to report a specific post
# once. if enabled, the user will not be informed
# that their second report on a post didn't go through,
# hopefully preventing them from spamming reports on an
# undeserving post.
silent_fail_on_double_report = false

[legacy.api_v1_interface]
# the legacy api is not going to get any new features
# and it cannot really benefit from the better efficiency
# of the modern one. it does get somewhat better image
# efficiency though, which is a definite plus.
enable = false
# api v1 doesn't have an interface for providing a pixel ratio
# so we can't optimize images there. you can define a default here.
# 2 is a somewhat sane default, since a lot of people are on phones
# with high dpi screens now
image_pixel_ratio = 2
signup_enabled = false
"""

"""
    _load_toml
    
    Loads a string containing a TOML file, into an AttrDict,
    which allows for property access via dot notation.
"""


def _load_toml(toml_string: str) -> AttrDict:
    return AttrDict(toml.loads(toml_string))


"""
    _load_config
    
    Loads a given configuration file.
"""


def _load_config(filename: str) -> AttrDict:
    console.log(f"Trying to load configuration file from {filename}...")
    with open(filename, 'r') as config_file:
        return _load_toml(config_file.read())


"""d
    _create_config
    
    Creates a given configuration file with given content.
"""


def _create_config(filename: str, content: str) -> None:
    with open(filename, 'w') as config_file:
        config_file.write(content)


"""
    _create_or_load_config
    
    If the configuration exists, load it. Otherwise create it and load it.
"""


def _create_or_load_config(filename: str):
    # write the default config to the given filename
    # if it doesn't already exist
    if not os.path.exists(filename):
        _create_config(filename, DEFAULT_CONFIG)
        console.log(f"Default configuration file created at {filename}.")
    return _load_config(filename)


config = _create_or_load_config(CONFIG_PATH)

print(config)
