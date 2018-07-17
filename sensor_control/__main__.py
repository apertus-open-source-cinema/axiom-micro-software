import os
import fire
from importlib import import_module
from sensor_control.wrappers import CliWrapper

def get_wrapper(wrapper="CliWrapper", sensor="Ar0330"):
    import sensor_control.wrappers
    sensor_mod = import_module("sensor_control." + sensor.lower() + "." + sensor.lower())

    wrapper = getattr(sensor_control.wrappers, wrapper)
    sensor = getattr(sensor_mod, sensor)
    return wrapper(sensor)

def main(noreset=False):
    from sensor_control.ar0330.ar0330 import Ar0330 as Sensor

    if noreset:
        def nop(*args, **kwargs):
            pass
        Sensor._reset = nop

    fire.Fire(get_wrapper)

if __name__ == "__main__":
    kwargs = {}
    if os.environ.get("SENSORCTL_NORESET", 0):
        kwargs["noreset"] = True
        
    main(**kwargs)
