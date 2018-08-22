from yaml import load
from os.path import dirname, join


class Config:
    def __init__(self, filename='config.yml'):
        self.conf = load(open(join(dirname(__file__), "config.yml")))

    def __getattr__(self, item):
        return self.conf[item]
