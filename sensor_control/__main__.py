import os
import fire
from yaml import load
from importlib import import_module
from sensor_control.util import RelativeOpener

relative_opener = RelativeOpener(__file__)
conf = load(relative_opener.open("config.yml"))

def get_wrapper(wrapper="CliWrapper", sensor=None):
    import sensor_control.wrappers
    if sensor is None:
        sensor = conf["sensor"]
    sensor_mod = import_module("sensor_control." + sensor.lower() + "." + sensor.lower())

    wrapper = getattr(sensor_control.wrappers, wrapper)
    sensor = getattr(sensor_mod, sensor)
    return wrapper(sensor)

def main():
    fire.Fire(get_wrapper)

if __name__ == "__main__":
    main()
