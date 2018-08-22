#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from conf import Config
from app import app

if __name__ == '__main__':
    conf = Config()
    WSGIServer(app, bindAddress=conf.fastcgi_socket).run()
