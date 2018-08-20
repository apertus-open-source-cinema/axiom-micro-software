import errno
import logging

from fuse import FUSE, Operations, LoggingMixIn


class PropFS(Operations, LoggingMixIn):
    """
    Expose a hierarchy of Objects as a filesystem with a given set of rules
    """

    def __init__(self, target):
        self.target = target

    # util methods for exploring the target
    def _get_object(self, path):
        """
        Converts a path to the right python object in the self.target tree

        :param path: the path string
        :returns: the object that is adressed with the path
        """
        parts = path[1:].split("/")
        if len(parts) == 1:
            return self.target

        last = self.target
        for part in parts:
            last = getattr(last, part)
        return last

    # the real fuse operations
    def readdir(self, path, fh):
        obj = self._get_object(path)
        children = dir(obj)
        children = filter(lambda attr: type(getattr(obj, attr)) != staticmethod and attr[0] != "_", children)

        return ['.', '..'] + list(children)

    def read(self, path, size, offset, fh):
        try:
            val = str(self._get_object(path)) + '\n'
        except:
            return -errno.ENOENT

        str_len = len(val)
        if offset < str_len:
            if offset + size > str_len:
                size = str_len - offset
            buf = val[offset:offset + size]
        else:
            buf = ''
        return buf

    def write(self, path, data, offset, fh):
        assert offset == 0

        try:
            val = self._get_object(path)
        except:
            return -errno.ENOENT
        return len(data)


def expose_properties(target, mountpoint):
    logging.basicConfig(level=logging.DEBUG)
    return FUSE(PropFS(target), mountpoint, foreground=True)
