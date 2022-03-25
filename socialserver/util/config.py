#  Copyright (c) Niall Asher 2022

import os
import toml
from socialserver.util.output import console
from pathlib import Path
from socialserver.util.namespace import dict_to_simple_namespace
from socialserver.constants import ROOT_DIR
from types import SimpleNamespace
from string import Template

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

with open(f"{ROOT_DIR}/resources/default_config.toml", "r") as config_file:
    DEFAULT_CONFIG = Template(config_file.read()).substitute({"FILE_ROOT": FILE_ROOT})

"""
    _test_config
    
    Tests a loaded dict against an example configuration dict. 
    (To test against the default schema, parse it, then use the
    resultant dict as the second argument)
    
    Will exit program with an error code of 1 if keys are missing.
"""


# FIXME: this doesn't actually work since removing attrdict, but I want to replace it anyway. Will do soon.
def _test_config(current_config: SimpleNamespace, schema: SimpleNamespace) -> None:
    # Data isn't validated, just structure, so feel free to use a loaded
    # copy of DEFAULT_CONFIG as your schema.

    def _recursive_unwrap_ns_keys(dict_obj: SimpleNamespace, prefix=""):
        keys = []
        for dict_key in vars(dict_obj).keys():
            keys.append(prefix + dict_key)
            # if type == dict we're dealing with a nested one,
            # so we'll recurse using it as the base, with an
            # updated prefix
            if type(vars(dict_obj).get(dict_key)) is dict:
                nested_keys = _recursive_unwrap_ns_keys(
                    dict_obj.get(dict_key), prefix=(prefix + dict_key + ".")
                )
                for nested_key in nested_keys:
                    keys.append(nested_key)
        return keys

    current_config_keys = _recursive_unwrap_ns_keys(current_config)
    schema_config_keys = _recursive_unwrap_ns_keys(schema)

    # check for any keys that are in the schema,
    # but *not* in current_config_keys. exit if
    # any are missing, since dying now is preferable
    # to a crash when the user touches functionality
    # that checks for a key. in the future, it might be
    # nice to have default values instead?

    missing_keys = []

    for key in schema_config_keys:
        if key not in current_config_keys:
            console.log(
                f"[bold red]Missing key in configuration file:[/bold red][italic] {key}"
            )
            missing_keys.append(key)

    if len(missing_keys) >= 1:
        console.log(
            ":dizzy_face: The config file is missing keys! Cannot continue.", emoji=True
        )
        exit(1)


"""
    _load_toml
    
    Loads a string containing a TOML file, into a SimpleNamespace,
    which allows for property access via dot notation.
"""


def _load_toml(toml_string: str) -> SimpleNamespace:
    dt = dict(toml.loads(toml_string))
    return dict_to_simple_namespace(dt)


"""
    _load_config
    
    Loads a given configuration file, testing it in the process.
"""


def _load_config(filename: str) -> SimpleNamespace:
    console.log(f"Trying to load configuration file from {filename}...")
    with open(filename, "r") as config_file:
        config_data = config_file.read()
        config_dict = _load_toml(config_data)

        _test_config(config_dict, _load_toml(DEFAULT_CONFIG))
        console.log("Configuration file OK!")

        return config_dict


"""
    _create_config
    
    Creates a given configuration file with given content.
"""


def _create_config(filename: str, content: str) -> None:
    with open(filename, "w") as config_file:
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


# if you want to use the configuration in another file,
# just import config from here.

config = _create_or_load_config(CONFIG_PATH)
