import os.path


class RelativeOpener:
    """ Provide open() relative to a given absolute base path"""

    def __init__(self, base_path):
        self.base_path = os.path.dirname(base_path)

    def open(self, path, *args, **kwargs):
        p = os.path.join(self.base_path, path)
        return open(p, *args, **kwargs)
