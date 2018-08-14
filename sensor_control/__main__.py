import os
import sys
import argparse
from yaml import load
from importlib import import_module
from sensor_control.util import RelativeOpener
from sensor_control.propfs import expose_properties

relative_opener = RelativeOpener(__file__)
conf = load(relative_opener.open("config.yml"))

def get_sensor(sensor):
    sensor_mod = import_module("sensor_control." + sensor.lower() + "." + sensor.lower())

    sensor = getattr(sensor_mod, sensor)
    return sensor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sensor', default=conf["sensor"])
    parser.add_argument('fuseargs', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    sensor = get_sensor(args.sensor)()

    # fuse-python eats sys.argv, so we just shove the rest of the args there
    args.fuseargs.insert(0, sys.argv[0])
    sys.argv = args.fuseargs
    breakpoint()
    expose_properties(sensor)

if __name__ == "__main__":
    main()
