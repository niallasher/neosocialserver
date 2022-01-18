from types import SimpleNamespace
from copy import copy

"""
    dict_to_simple_namespace
    
    take a dict and convert it (along with it's nested elements) to
    a SimpleNamespace.
"""


def dict_to_simple_namespace(dict_obj: dict) -> SimpleNamespace:
    ns = SimpleNamespace()
    for x in dict_obj:
        if isinstance(dict_obj.get(x), dict):
            setattr(ns, x, dict_to_simple_namespace(dict_obj.get(x)))
        else:
            setattr(ns, x, dict_obj.get(x))
    return ns
