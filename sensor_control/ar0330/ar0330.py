from sensor_control.sensor import Sensor
from sensor_control.i2c import I2c
from sensor_control.gpio import GPIO
from sensor_control.util import RelativeOpener
from yaml import load


class Ar0330(Sensor):
    def __init__(self):
        # __file__ refers to the absolute path of this file
        # This is needed because the builtin open() is relative to the current working directory
        self._ro = RelativeOpener(__file__)
        self.open = self._ro.open

        self.i2c = I2c("1")
        self.gpio = GPIO(0x41200000)
        self.register_map = load(self.open("registers.yml"))

        # reset and initialize sensor
        self._reset()

    def get_resolution(self):
        pass

    def set_window(self, xmin, ymin, xmax, ymax):
        pass

    def set_skipping(self, x, y):
        pass

    def set_binning(self, x, y):
        pass

    def set_frame_rate(self, fps):
        pass

    def set_exposure_time(self, ms):
        pass

    def set_analog_gain(self, multiply):
        pass

    def set_digital_gain(self, multiply):
        pass

    def set_color_gains(self, r, g1, g2, b):
        pass

    def _read(self, register_name):
        register = self.register_map[register_name]
        addr = register["address"]
        count = register["width"]
        addr_high = addr >> 8
        addr_low = addr & 0xff
        cmd = "w2@%d %d %d r%d" % (address, addr_high, addr_low, count)
        return self.i2c.transfer(cmd)

    def _write(self, register_name, value):
        register = self.register_map[register_name]
        addr = register["address"]
        count = register["width"]
        addr_high = addr >> 8
        addr_low = addr & 0xff
        write_value = []

        for v in range(1, count + 1):
            write_value.append("0x%x" % (value & 0xff))
            value >>= 8

        values = " ".join(reversed(write_value))
        cmd = "w%d@%d %d %d %s" % (2 + count, address, addr_high, addr_low, values)
        return self.i2c.transfer(cmd)

    def _reset(self):
        # toggle reset pin (active low)
        self.gpio.set(0x7)
        sleep(.1)
        self.gpio.set(0x0)
        sleep(.1)
        self.gpio.set(0x7)
        sleep(.1)

        # magic init
        _write("magic_init_config", 0xa114)
        _write("magic_init_start", 0x0070)
        sleep(.1)

        # check chip_version
        chip_version = _read("chip_version")
        if chip_version != self.register_map["chip_version"]["value"]:
            raise ValueError("Chip version mismatch: got {}, config is for {}".format(
                chip_version, self.register_map["chip_version"]["value"]))

        self._reversed_chiprev = _read("reversed_chiprev")
        self._version = _read("test_data_red")

