import errno
import logging
from functools import lru_cache
from stat import S_IFDIR, S_IFREG

from fuse import FUSE, Operations, LoggingMixIn, FuseOSError, ENOENT


class PropFS(Operations, LoggingMixIn):
    """
    Expose a the getters and setters of a hierarchy of Objects as a filesystem
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
        if path == "/":
            return self.target

        parts = path[1:].split("/")
        last = self.target
        for part in parts:
            if type(last) == dict:
                last = last[part]
            else:
                last = getattr(last, "get_" + part)()
        return last

    @lru_cache(maxsize=None)
    def _is_file(self, path):
        obj = self._get_object(path)
        return type(obj) in (int, float, bool, str)

    @lru_cache(maxsize=None)
    def _get_required_type(self, path):
        return type(self._get_object(path))

    # the real fuse operations
    def open(self, path, flags):
        return 0

    def getattr(self, path, fh=None):
        try:
            obj = self._get_object(path)
        except (AttributeError, KeyError):
            raise FuseOSError(ENOENT)

        return dict(
            st_mode=((S_IFREG if self._is_file(path) else S_IFDIR) | 0o777),
            st_nlink=2,
            st_size=1024,
            st_ctime=0,
            st_mtime=0,
            st_atime=0)

    def readdir(self, path, fh=None):
        obj = self._get_object(path)
        if type(obj) == dict:
            children = obj.keys()
        else:
            children = dir(obj)
            children = filter(lambda attr: attr.startswith("get_"), children)
            children = [child[len("get_"):] for child in children]

        return ['.', '..'] + list(children)

    def read(self, path, size, offset, fh=None):
        try:
            val = str(self._get_object(path)) + '\n'
        except (AttributeError, KeyError):
            return -errno.ENOENT

        str_len = len(val)
        if offset < str_len:
            if offset + size > str_len:
                size = str_len - offset
            buf = val[offset:offset + size]
        else:
            buf = ''
        return buf.encode("UTF-8")

    def write(self, path, data, offset, fh=None):
        assert offset == 0

        try:
            val = self._get_required_type(path)(data)
        except ValueError:
            return -errno.EINVAL

        path_elements = path.split("/")

        try:
            start_path = "/".join(path_elements[0:-1])
            obj = self._get_object(start_path)
            getattr(obj, "set_" + path_elements[-1])(val)
        except AttributeError:
            # we are writing to a dict
            before = self._get_object("/".join(path_elements[0:-1]))
            setter = getattr(self._get_object("/".join(path_elements[0:-2])), "set_" + path_elements[-2])
            before[path_elements[-1]] = val
            setter(**before)
        return len(data)

    def truncate(self, path, length, fh=None):
        # truncate is needed to indicate, that the fs is not read only
        pass



def expose_properties(target, mountpoint):
    logging.basicConfig(level=logging.DEBUG)
    return FUSE(PropFS(target), mountpoint, foreground=False)
