
from importlib import import_module

def main():
    from sensor_control.ar0330.ar0330 import Ar0330 as Sensor
    s = Sensor()

if __name__ == "__main__":
    main()
