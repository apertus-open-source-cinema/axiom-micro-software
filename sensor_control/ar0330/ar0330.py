from sensor_control.sensor import Sensor
from sensor_control.i2c import I2c
from sensor_control.gpio import GPIO
from sensor_control.pll import optimal_pll_config
from sensor_control.util import RelativeOpener

import analog_gain

from yaml import load


class Ar0330(Sensor):
    def __init__(self):
        # __file__ refers to the absolute path of this file
        # This is needed because the builtin open() is relative to the current working directory
        self._ro = RelativeOpener(__file__)
        self.open = self._ro.open

        self.extclk = 24000000
        self.i2c = I2c("1")
        self.gpio = GPIO(0x41200000)
        self.register_map = load(self.open("registers.yml"))

        # reset and initialize sensor
        self._reset()

    def get_resolution(self):
        # this is the maximum in video mode
        # still mode supports a higher ymax
        return (2304, 1296)

    def set_window(self, xmin, ymin, xmax, ymax):
        s_xmax, s_ymax = self.get_resolution()
        if xmax > s_xmax or ymax > s_ymax:
            raise ValueError("Window outside maximum resolution")
        xstart = xmin + 6
        xend = xmax + 6
        ystart = ymin + 6
        yend = ymax + 6

        self._write("x_addr_start", xstart)
        self._write("x_addr_end", xend)
        self._write("y_addr_start", ystart)
        self._write("y_addr_end", yend)

        # Todo: line_length_pck and frame_length_lines (with extra_delay) determine the frame rate depending on the window size

    def set_skipping(self, x, y):
        pass

    def set_binning(self, x, y):
        pass

    def set_frame_rate(self, fps):
        pass

    def set_exposure_time(self, ms):
        pass

    def set_analog_gain(self, multiply):
        actual, coarse, fine = analog_gain.get_close(multiply)
        val = int(format(coarse, '02b') + format(fine, '04b'), base=2)
        self._write("analog_gain", val)
        return actual

    def set_digital_gain(self, multiply):
        base = int(multiply)
        fraction = int((multiply % 1.0) * 128)
        val = int(format(base, '04b') + format(fraction, '07b'), base=2)
        self._write("global_gain", val)
        return multiply

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
        self._write("magic_init_config", 0xa114)
        self._write("magic_init_start", 0x0070)
        sleep(.1)

        # check chip_version
        chip_version = _read("chip_version")
        if chip_version != self.register_map["chip_version"]["value"]:
            raise ValueError("Chip version mismatch: got {}, config is for {}".format(
                chip_version, self.register_map["chip_version"]["value"]))

        self._reversed_chiprev = _read("reversed_chiprev")
        self._version = _read("test_data_red")

        # pll config for 12bit, 4 lane hispi
        vco_hispi_4lanes_12bit_clk = 588000000 # 588 MHz
        pll_config = optimal_pll_config(self.extclk, vco_hispi_4lanes_12bit_clk)
        pre_pll_clk_div = pll_config["pre_pll_clk_div"] 
        pll_multiplier = pll_config["pll_multiplier"] 

        # taken from table in datasheet, no idea how to calculate on our own
        vt_sys_clk_div =  1
        vt_pix_clk_div =  6
        op_sys_clk_div =  1
        op_pix_clk_div = 12

        self._write("vt_pix_clk_div", vt_pix_clk_div)
        self._write("vt_sys_clk_div", vt_sys_clk_div)
        self._write("pre_pll_clk_div", pre_pll_clk_div)
        self._write("pll_multiplier", pll_multiplier)
        self._write("op_pix_clk_div", op_pix_clk_div)
        self._write("op_sys_clk_div", op_sys_clk_div)

        # pll lock time
        sleep(.1)

        # data format setting
        ## 0xc0c - 12bit raw uncompressed
        # TODO: move to profile
        self._write("data_format_bits", 0x0c0c)
        # serial output format
        ## select hivcm (1V8)
        self._write("datapath_select", 1 << 9);
        ## lol ????
        self._write("mipi_config_status", 0xc00d);
