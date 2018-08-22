from flask import Flask, request, abort
from conf import Config
from os.path import join
from os import walk
from json import dumps
import errno

app = Flask(__name__)
conf = Config()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'PUT'])
def catch_all(path):
    if request.method == 'PUT':
        try:
            write_file(join(conf.driver_mountpoint, path), request.stream.read())
        except OSError as e:
            if e.errno == 30:
                abort(404)
            elif e.errno == 22:
                abort(400)
            else:
                abort(500)
    try:
        return read_file(join(conf.driver_mountpoint, path))
    except IsADirectoryError:
        return list_directory(join(conf.driver_mountpoint, path))
    except FileNotFoundError:
        abort(404)


def read_file(path):
    with open(path) as f:
        return f.read()


def write_file(path, val):
    with open(path, 'w') as f:
        f.write(val.decode('UTF-8'))


def list_directory(path):
    obj = {}
    files = walk(path)
    for walk_path, dirs, files in files:
        print(dirs, files)
        split_path = filter(lambda x: x != '', walk_path[len(path):].split("/"))
        curr = obj
        for part in split_path:
            curr=curr[part]

        for dir in dirs:
            curr[dir] = {}
        for file in files:
            curr[file] = read_file(join(walk_path, file)).strip()
    return dumps(obj, indent='\t')
