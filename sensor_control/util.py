import os.path
import re

class RelativeOpener:
    """ Provide open() relative to a given absolute base path"""
    def __init__(self, base_path):
        self.base_path = os.path.dirname(base_path)

    def open(self, path, *args, **kwargs):
        p = os.path.join(self.base_path, path)
        return open(p, *args, **kwargs)

def to(converter):
    def decorator(fun):
        def wrapper(self, value):
            value = converter(value)
            return fun(self, value)
        return wrapper
    return decorator


def to_tuple(converter, length):
    def _parse_tupel(value):
        if isinstance(value, tuple):
            return value

        value = value.strip()
        if not (value[0] == "(" and value[-1] == ")"):
            raise ValueError("Tupel needs to start and end with parenthesis")
        value = value[1:-1]
        value = value.replace(" ", "")
        value = value.split(",")
        if len(value) != length:
            raise ValueError("Tuple of wrong lenth")

        l = [converter(v) for v in value]
        return tuple(l)

    return to(_parse_tupel)
