import argparse
from importlib import import_module

from stringcase import pascalcase, snakecase
from yaml import load

from camera_control.propfs.propfs import expose_properties
from camera_control.util.relative_opener import RelativeOpener

relative_opener = RelativeOpener(__file__)
conf = load(relative_opener.open("config.yml"))


class Camera:
    def __init__(self, sensor_name):
        self.sensor = self.get_sensor(sensor_name)

    @staticmethod
    def get_sensor(sensor):
        sensor_mod = import_module("camera_control.sensor." + snakecase(sensor) + "." + snakecase(sensor))

        sensor = getattr(sensor_mod, pascalcase(sensor))
        return sensor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sensor', default=conf["sensor"])
    parser.add_argument('-m', '--mount-point', default=conf["mount_point"])
    args = parser.parse_args()

    camera = Camera(args.sensor)
    expose_properties(camera, args.mount_point)
