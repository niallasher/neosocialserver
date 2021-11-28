import json
from types import SimpleNamespace
from os import path
from rich import print
from copy import copy


"""
	configutil.py
	Utilities for managing config files, including loading, saving, and accessing as a SimpleNamespace.
"""


CONFIG_FILE_PATH = "./config.json"

# default_config also serves as a schema
# for the config keys
DEFAULT_CONFIG = {
    "network": {
        "host": "0.0.0.0",
        "port": 80
    },
    "debug": {
        "enable_flask_debug_mode": False,
        "auto_reload_templates": False,
        "zero_max_file_age": False
    }
}

# reserved keys. i.e. keys that cannot be used in
# a valid config
RESERVED_KEYS = [".save"]

"""
	verify_config_against_schema: verify the configuration file contains the same keys as schema

	Parameters:
		namespace: SimpleNamespace, config object to check.
		schema: dict, dict containing the required keys. can use DEFAULT_CONFIG (value types aren't checked yet)
"""


def verify_config_against_schema(namespace, schema) -> None:

    ns_dict = dump_namespace_to_dict(namespace)

    """
		recursive_unwrap_dict_keys: loop through a dict, adding all it's keys to a list, formatted for readability.
		handles dicts within dicts (due to nested objects in json), by calling itself on the nested dict when encountered
		(syntax inspired by jq)

		Parameters:
			dict_object: dict, dict to unwrap
			prefix: optional, string, string to prefix key with (no need to change this manually).
	"""
    def recursive_unwrap_dict_keys(dict_object, prefix="."):
        # TODO: see if there is some way to do this in the standard library
        keys = []
        for key in dict_object.keys():
            keys.append(prefix + key)
            # go through all dicts inside the dict and so on/so forth
            if type(dict_object.get(key)) == dict:
                exkeys = (recursive_unwrap_dict_keys(
                    dict_object.get(key), prefix=(prefix + key + ".")))
                for exkey in exkeys:
                    keys.append(exkey)
        return keys

    schema_keys = recursive_unwrap_dict_keys(schema)
    ns_dict_keys = recursive_unwrap_dict_keys(ns_dict)

    missing_keys = []
    extraneous_keys = []
    illegal_keys = []

    # check for missing keys
    for schema_key in schema_keys:
        if schema_key not in ns_dict_keys:
            missing_keys.append(schema_key)
    # check for extra keys & illegal keys with reserved names
    for ns_dict_key in ns_dict_keys:
        if ns_dict_key in RESERVED_KEYS:
            illegal_keys.append(ns_dict_key)
        elif ns_dict_key not in schema_keys:
            extraneous_keys.append(ns_dict_key)

    config_perfect = True if (len(extraneous_keys)
                              + len(missing_keys)
                              + len(illegal_keys)) == 0 else False

    for key in extraneous_keys:
        print(f"Extraneous/Unused key: {key}")
    for key in missing_keys:
        print(f"Required key missing: {key}")
    for key in illegal_keys:
        print(f"Illegal key name: {key}")

    if len(illegal_keys) + len(missing_keys) >= 1:
        print("Unresolvable issues with configuration.")
        print("Please check it carefully.")
        # exiting with non-0 exit code,
        # since we can't continue running
        # with a malformed config.
        exit(1)


"""
	persist_config_namespace: save the changed namespace to the disk as json

	Parameters:
		namespace: SimpleNamespace, the namespace to be saved
"""


def persist_config_namespace(namespace) -> None:
    # shallow copy the namespace
    ns = copy(namespace)
    # strip the save key from the new one
    del(ns.save)
    config_dict = dump_namespace_to_dict(ns)
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        config_file.write(
            json.dumps(
                config_dict,
                indent=2
            )
        )


"""
	load_json_to_namespace: load unprocessed json to a SimpleNamespace

	Parameters:
		data: str, raw text data containing unprocessed json, to be converted
"""


def load_json_to_namespace(data) -> SimpleNamespace:
    return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


"""
		dump_namespace_to_dict: convert a SimpleNamespace to a dict, handling nesting

	Parameters:
		namespace: SimpleNamespace, namespace to be converted
"""


def dump_namespace_to_dict(namespace) -> dict:
    nsc = copy(namespace)
    ns = vars(nsc)
    for x in ns:
        if type(ns.get(x)) == SimpleNamespace:
            ns[x] = dump_namespace_to_dict(ns.get(x))
    return ns


"""
	_load_config: load CONFIG_FILE_PATH into a namespace, then return it.
	This shouldn't be called directly, use load_or_create_config to handle missing config.
"""


def _load_config() -> SimpleNamespace:
    with open(CONFIG_FILE_PATH, 'r') as config_file:
        return load_json_to_namespace(config_file.read())


"""
	load_or_create_config: load the config if it exists, else create it
"""


def load_or_create_config():
    if path.exists(CONFIG_FILE_PATH):
        namespace = _load_config()
        verify_config_against_schema(namespace, DEFAULT_CONFIG)
        # insert a reference to the save function.
        # (this won't conflict; save is in schema checkers reserved_keys array)
        namespace.save = lambda: persist_config_namespace(namespace)
        return namespace
    else:
        # load default config, and save it to disk.
        print("Using default config...")
        # insert ref to the save function then call it.
        namespace = load_json_to_namespace(json.dumps(DEFAULT_CONFIG))
        namespace.save = lambda: persist_config_namespace(namespace)
        namespace.save()
        return namespace


config = load_or_create_config()

if __name__ == "__main__":
    config = load_or_create_config()
    print(config)
