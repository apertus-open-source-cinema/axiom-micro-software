import os
import fire
from importlib import import_module
from sensor_control.prop_methods import CliWrapper

def main(noreset=False):
    from sensor_control.ar0330.ar0330 import Ar0330 as Sensor

    if noreset:
        def nop(*args, **kwargs):
            pass
        Sensor._reset = nop

    s = CliWrapper(Sensor)
    fire.Fire(s)

if __name__ == "__main__":
    kwargs = {}
    if os.environ.get("SENSORCTL_NORESET", 0):
        kwargs["noreset"] = True
        
    main(**kwargs)
