from sensor_control.sensor import Sensor
from sensor_control.i2c import I2c
from sensor_control.gpio import GPIO
from sensor_control.pll import optimal_pll_config
from sensor_control.util import RelativeOpener

import sensor_control.ar0330.analog_gain as analog_gain

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

    @property
    def resolution(self):
        # this is the maximum in video mode
        # still mode supports a higher ymax
        return (2304, 1296)

    @property
    def window(self):
        xmin = self._read("x_addr_start")
        ymin = self._read("y_addr_start")
        xmax = self._read("x_addr_end")
        ymax = self._read("y_addr_end")
        return (xmin, ymin, xmax, ymax)

    @window.setter
    def window(self, value):
        xmin, ymin, xmax, ymax = value

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

    def _get_skipbin(self, axis):
        if axis == "x":
            colrow = "col"
        elif axis == "y":
            colrow = "row"
        else:
            raise ValueError("Axis is either x or y")

        inc = self._read(axis + "_odd_inc")
        skip_factor = (1 + inc) / 2
        analog_bin = self._read(colrow + "_sf_bin_en")
        digital_bin = self._read(colrow + "_bin")
        if analog_bin != 0:
            binning = 1
        elif digital_bin != 0:
            binning = 2
        else:
            binning = 0

        return skip_factor, binning

    def _check_skip(self, axis, skip):
        # See ar0330 datasheet p. 35
        end = self._read(axis + "_addr_end")
        start = self._read(axis + "_addr_start")

        n = (end - start + 1) / (skip/2)
        if n % 2 == 0:
            return True
        else:
            return False

    def _set_skipbin(self, axis, skip, bin_):
        if axis == "x":
            colrow = "col"
        elif axis == "y":
            colrow = "row"
        else:
            raise ValueError("Axis is either x or y")

        if self._check_skip(skip, axis) is False:
            raise ValueError("Skipping/Binning not supported for this resolution, try changing by one or a few pixels")

        inc = (skip * 2) - 1
        self._write(axis + "_odd_inc", inc)

        self._write(colrow + "_sf_bin_en", 0)
        self._write(colrow + "_bin", 0)
        if bin_ == 1:
            self._write(colrow + "_sf_bin_en", 1)
        elif bin_ == 2:
            self._write(colrow + "_bin", 1)

    @property
    def skipping(self):
        x_skip, x_bin = self._get_skipbin("x")
        y_skip, y_bin = self._get_skipbin("y")

        # ignore skipping value if binning is also enabled
        if x_bin != 0:
            x_skip = 0
        if y_bin != 0:
            y_skip = 0

        return x_skip, y_skip

    @skipping.setter
    def skipping(self, value):
        x, y = value
        self._set_skipbin("x", x, 0)
        self._set_skipbin("y", y, 0)

    @property
    def binning(self):
        x_skip, x_bin = self._get_skipbin("x")
        y_skip, y_bin = self._get_skipbin("y")

        # zero out skipping value if only skipping and no binning is active
        if x_bin == 0:
            x_skip = 0
        if y_bin != 0:
            y_skip = 0

        return x_skip, y_skip

    @binning.setter
    def binning(self, value):
        x, y = value
        # use 2 for digital binning
        self._set_skipbin("x", x, 1)
        self._set_skipbin("y", y, 1)

    def _get_clk_pix(self):
        clk_pix = ((self.extclk / self._read("pre_pll_clk_div")) * 
                self._read("pll_multiplier")) / self._read("vt_sys_clk_div") 
        return clk_pix

    @property
    def frame_rate(self):
        clk_pix = self._get_clk_pix()
        t_frame = (1 / clk_pix) * (self._read("frame_length_lines") * self._read("line_length_pck") * self._read("extra_delay"))

        return 1 / t_frame

    @frame_rate.setter
    def frame_rate(self, fps):
        pass

    @property
    def exposure_time(self):
        # technically, integration time since we don't have a shutter
        clk_pix = self._get_clk_pix()
        t_row = self._read("line_length_pck") / clk_pix
        t_coarse = self._read("coarse_integration_time") * t_row
        t_fine = self._read("fine_integration_time") / clk_pix
        return t_coarse - t_fine

    @exposure_time.setter
    def exposure_time(self, ms):
        pass

    @property
    def analog_gain(self):
        pass

    @analog_gain.setter
    def analog_gain(self, multiply):
        multiply = float(multiply)
        actual, coarse, fine = analog_gain.get_close(multiply)
        val = int(format(coarse, '02b') + format(fine, '04b'), base=2)
        self._write("analog_gain", val)
        return actual

    @property
    def digital_gain(self):
        pass

    @digital_gain.setter
    def digital_gain(self, multiply):
        base = int(multiply)
        fraction = int((multiply % 1.0) * 128)
        val = int(format(base, '04b') + format(fraction, '07b'), base=2)
        self._write("global_gain", val)
        return multiply

    @property
    def color_gains(self):
        pass

    @color_gains.setter
    def color_gains(self, value):
        r, g1, g2, b = value
        pass

    def _read(self, register_name):
        register = self.register_map[register_name]
        addr = register["address"]
        count = register["width"]
        addr_high = addr >> 8
        addr_low = addr & 0xff
        cmd = "w2@%d %d %d r%d" % (addr, addr_high, addr_low, count)
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
        cmd = "w%d@%d %d %d %s" % (2 + count, addr, addr_high, addr_low, values)
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
