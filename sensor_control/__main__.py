import os
import fire
from importlib import import_module

def get_wrapper(wrapper="CliWrapper", sensor="Ar0330"):
    import sensor_control.wrappers
    sensor_mod = import_module("sensor_control." + sensor.lower() + "." + sensor.lower())

    wrapper = getattr(sensor_control.wrappers, wrapper)
    sensor = getattr(sensor_mod, sensor)
    return wrapper(sensor)

def main():
    fire.Fire(get_wrapper)

if __name__ == "__main__":
    main()
