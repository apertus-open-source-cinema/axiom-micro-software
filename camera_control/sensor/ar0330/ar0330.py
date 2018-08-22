from time import sleep

from yaml import load

from camera_control.sensor.ar0330.util import optimal_pll_config, analog_gain_to_reg, reg_to_analog_gain, colrow
from camera_control.util.gpio import GPIO
from camera_control.util.i2c import I2c
from camera_control.util.relative_opener import RelativeOpener


class Ar0330():
    def __init__(self):
        # __file__ refers to the absolute path of this file
        # This is needed because the builtin open() is relative to the current working directory
        self._ro = RelativeOpener(__file__)
        self.open = self._ro.open

        self.extclk = 24000000
        self.i2c = I2c("0")
        self.gpio = GPIO(0x41200000)
        self.register_map = load(self.open("registers.yml"))

        # reset and initialize sensor
        self._reset()

    def get_resolution(self):
        # this is the maximum in video mode
        # still mode supports a higher ymax
        return dict(width=2304, height=1296)

    def get_window(self):
        x_start = self._read("x_addr_start")
        y_start = self._read("y_addr_start")
        x_end = self._read("x_addr_end")
        y_end = self._read("y_addr_end")
        return dict(x_start=x_start, y_start=y_start, x_end=x_end, y_end=y_end)

    def set_window(self, x_start, y_start, x_end, y_end):
        s_xmax, s_ymax = self.get_resolution()
        if x_end > s_xmax or y_end > s_ymax:
            raise ValueError("Window outside maximum resolution")

        xstart = x_start + 6
        xend = x_end + 6
        ystart = y_start + 6
        yend = y_end + 6

        self._write("x_addr_start", xstart)
        self._write("x_addr_end", xend)
        self._write("y_addr_start", ystart)
        self._write("y_addr_end", yend)

        # TODO: line_length_pck and frame_length_lines (with extra_delay) determine the frame rate depending on the window size

    def _get_skipbin(self, axis):
        cr = colrow(axis)
        inc = self._read(axis + "_odd_inc")
        skip_factor = (1 + inc) / 2
        analog_bin = self._read(cr + "_sf_bin_en")
        digital_bin = self._read(cr + "_bin")
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
        cr = colrow(axis)
        if self._check_skip(skip, axis) is False:
            raise ValueError("Skipping/Binning not supported for this resolution, try changing by one or a few pixels")

        inc = (skip * 2) - 1
        self._write(axis + "_odd_inc", inc)

        self._write(cr + "_sf_bin_en", 0)
        self._write(cr + "_bin", 0)
        if bin_ == 1:
            self._write(cr + "_sf_bin_en", 1)
        elif bin_ == 2:
            self._write(cr + "_bin", 1)

    def get_skipping(self):
        x_skip, x_bin = self._get_skipbin("x")
        y_skip, y_bin = self._get_skipbin("y")

        # ignore skipping value if binning is also enabled
        if x_bin != 0:
            x_skip = 0
        if y_bin != 0:
            y_skip = 0

        return dict(x_skip=x_skip, y_skip=y_skip)

    def set_skipping(self, x_skip, y_skip):
        self._set_skipbin("x", x_skip, 0)
        self._set_skipbin("y", y_skip, 0)

    def get_binning(self):
        x_skip, x_bin = self._get_skipbin("x")
        y_skip, y_bin = self._get_skipbin("y")

        return dict(xbin=x_bin, ybin=y_bin)

    def set_binning(self, x_bin, y_bin):
        # use 2 for digital binning
        self._set_skipbin("x", x_bin, 1)
        self._set_skipbin("y", y_bin, 1)

    def _get_clk_pix(self):
        clk_pix = ((self.extclk / self._read("pre_pll_clk_div")) * 
                self._read("pll_multiplier")) / self._read("vt_sys_clk_div") 
        return clk_pix

    def get_frame_rate(self):
        # TODO: fixme
        clk_pix = self._get_clk_pix()
        t_frame = (1 / clk_pix) * (self._read("frame_length_lines") * self._read("line_length_pck") + self._read("extra_delay"))
        return 1 / t_frame

    def set_frame_rate(self, fps):
        # TODO: Depending on resolution, frame_length_lines and line_length_pck can be set to lower(/est) values
        clk_pix = self._get_clk_pix()
        frame_length_lines = self._read("frame_length_lines")
        line_length_pck = self._read("line_length_pck")
        extra_delay = clk_pix / fps - frame_length_lines * line_length_pck
        extra_delay = max(int(extra_delay), 0)
        self._write("extra_delay", extra_delay)

    def get_exposure_time(self):
        # technically, integration time since we don't have a shutter
        clk_pix = self._get_clk_pix()
        t_row = self._read("line_length_pck") / clk_pix
        t_coarse = self._read("coarse_integration_time") * t_row
        t_fine = self._read("fine_integration_time") / clk_pix
        return float(t_coarse - t_fine) * 1000

    def set_exposure_time(self, ms):
        clk_pix = self._get_clk_pix()
        t_coarse = ms * 1000  # milliseconds -> microseconds
        t_row = self._read("line_length_pck") / clk_pix
        coarse_integration_time = t_coarse / t_row
        self._write("coarse_integration_time", int(coarse_integration_time))
        self._write("fine_integration_time", int(0))
        # as per recommendation (p.29), we're leaving fine_integration_time at 0

    def get_analog_gain(self):
        reg = self._read("analog_gain")
        return reg_to_analog_gain(reg)

    def set_analog_gain(self, multiply):
        multiply = float(multiply)
        val = analog_gain_to_reg(multiply)
        self._write("analog_gain", val)

    def get_digital_gain(self):
        val = self._read("global_gain")
        bits = "{0:012b}".format(val)
        return float(int(bits[0:3], base=2) + int(bits[4:11], base=2) / 128)

    def set_digital_gain(self, multiply):
        base = int(multiply)
        fraction = int((multiply % 1.0) * 128)
        val = int(format(base, '04b') + format(fraction, '07b'), base=2)
        self._write("global_gain", val)

    def get_color_gains(self):
        nan = float('nan')
        return dict(r=nan, g1=nan, g2=nan, b=nan)

    def set_color_gains(self, r, g1, g2, b):
        pass

    def _read(self, register_name):
        register = self.register_map[register_name]
        addr = register["address"]
        count = register["width"]
        addr_high = addr >> 8
        addr_low = addr & 0xff
        # TODO(robin): dont hardcode this (16) address
        cmd = "w2@%d %d %d r%d" % (16, addr_high, addr_low, count)
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
        # TODO(robin): dont hardcode this (16) address
        cmd = "w%d@%d %d %d %s" % (2 + count, 16, addr_high, addr_low, values)
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
        chip_version = self._read("chip_version")
        if chip_version != self.register_map["chip_version"]["value"]:
            raise ValueError("Chip version mismatch: got {}, config is for {}".format(
                chip_version, self.register_map["chip_version"]["value"]))

        self._version = self._read("test_data_red")

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
        self._write("datapath_select", 1 << 9)
        ## lol ????
        self._write("mipi_config_status", 0xc00d)
