#  Copyright (c) Niall Asher 2022

import os
from typing import Any, MutableMapping

from socialserver.util.output import console
from pathlib import Path
from socialserver.constants import ROOT_DIR
from socialserver.resources.config.schema import ServerConfig
from string import Template
from toml import loads, TomlDecodeError

# if the user doesn't specify a server root storage dir,
# we're going to store everything in $HOME/socialserver.

# TODO: need to see how this will work with containers and the like. (do they even have $HOME defined?)

HOME_DIR = os.getenv("HOME")

socialserver_root = os.getenv("SOCIALSERVER_ROOT", default=None)

if socialserver_root is None:
    console.log(
        f"$SOCIALSERVER_ROOT was not defined. Defaulting to {HOME_DIR}/socialserver!"
    )
    FILE_ROOT = f"{HOME_DIR}/socialserver"
else:
    console.log(f"Using root directory {socialserver_root}!")
    FILE_ROOT = socialserver_root

if not os.path.exists(FILE_ROOT):
    folder_path = Path(FILE_ROOT)
    folder_path.mkdir(parents=True)
    console.log(f"The root folder, {FILE_ROOT}, was created.")

DEFAULT_CONFIG_PATH = f"{FILE_ROOT}/config.toml"

CONFIG_PATH = os.getenv("SOCIALSERVER_CONFIG_FILE", default=DEFAULT_CONFIG_PATH)

with open(f"{ROOT_DIR}/resources/config/default_config.toml", "r") as config_file:
    DEFAULT_CONFIG = Template(config_file.read()).substitute({"FILE_ROOT": FILE_ROOT})

"""
    _toml_string_to_dict
    
    Converts a string containing valid TOML into a dict.
"""


def _load_toml(data: str) -> MutableMapping[str, Any]:
    try:
        return loads(data)
    except TomlDecodeError:
        console.log("Cannot parse configuration file; Not valid TOML!")
        exit(1)


"""
    _load_config
    
    Loads a given configuration file, testing it in the process.
"""


def _load_config(filename: str) -> ServerConfig:
    console.log(f"Trying to load configuration file from {filename}...")
    with open(filename, "r") as config_file:
        config_data = _load_toml(config_file.read())
        # pydantic handles the validation, so we just need to return the model.
        # any missing fields will raise an exception.
        return ServerConfig(**config_data)


"""
    _create_config
    
    Creates a given configuration file with given content.
"""


def _create_config(filename: str, content: str) -> None:
    with open(filename, "w") as new_config_file:
        new_config_file.write(content)


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


# if you want to use the configuration in another file,
# just import config from here.

config = _create_or_load_config(CONFIG_PATH)
