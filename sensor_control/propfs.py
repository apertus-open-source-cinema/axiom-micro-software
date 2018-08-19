#!/usr/bin/env python

#    Loosely based on python-fuse example hello.py, thanks!
#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    Licensed under GNU LGPL.
#

import os, stat, errno
import itertools
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class PropFS(Fuse):

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.props = {}
        self._get_props()
        Fuse.__init__(self, *args, **kwargs)

    def _get_props(self):
        cls = self.target.__class__
        for name, prop in cls.__dict__.items():
             if name[0] is not "_" and isinstance(prop, property):
                 self.props[name] = prop


    def getattr(self, path):
        prop = path[1:]
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2

        # strip first char which should? always be '/'
        elif prop in self.props.keys():
            st.st_mode = stat.S_IFREG | 0o666
            st.st_nlink = 1
            val = str(getattr(self.target, prop))
            st.st_size = len(val)
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        props = self.props.keys()
        for node in itertools.chain(('.', '..'), props):
            yield fuse.Direntry(node)

    def open(self, path, flags):
        if path[1:] not in self.props.keys():
            return -errno.ENOENT
        # we don't need to restrict write access:
        # if (flags & accmode) != os.O_RDONLY:
            # return -errno.EACCES

    def read(self, path, size, offset):
        prop = path[1:]
        if prop not in self.props.keys():
            return -errno.ENOENT
        val = str(getattr(self.target, prop))
        slen = len(val)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = val[offset:offset+size]
        else:
            buf = ''
        return buf

    def write(self, path, buf, offset):
        prop = path[1:]
        if prop not in self.props.keys():
            return -errno.EOENT
        val = str(getattr(self.target, prop))
        # TODO: handle offset
        setattr(self.target, prop, buf)
        return len(buf)

    def truncate(self, path, size):
        # needs to be implemented so bash file redirection works.
        # is pretty meaningless for our properties though and gets
        # over`write()`n anyways  ¯\_(ツ)_/¯
        return 0

def expose_properties(target):
    usage="""
Userspace hello example
""" + Fuse.fusage
    server = PropFS(target=target, version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()
