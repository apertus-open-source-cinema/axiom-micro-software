from sensor_control.sensor import Sensor
from sensor_control.i2c import I2c


class Ar0330(Sensor):
    def __init__(self):
        self.i2c = I2c("1")
        self.register_map =

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

