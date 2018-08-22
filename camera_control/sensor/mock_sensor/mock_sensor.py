class MockSensor():
    def __init__(self):
        width, height = self.get_resolution().values()
        self.window = dict(x_start=0, y_start=0, x_end=width, y_end=height)
        self.skipping = dict(x_skip=0, y_skip=0)
        self.binning = dict(x_binning=0, y_binning=0)
        self.frame_rate = 60.0
        self.exposure_time = 10.0
        self.analog_gain = 1.0
        self.digital_gain = 1.0
        self.color_gains = dict(r=1.0, g1=1.0, g2=1.0, b=1.0)

    def get_resolution(self):
        return dict(width=1280, height=720)

    def get_window(self):
        return self.window

    def set_window(self, x_start, y_start, x_end, y_end):
        x_max, y_max = self.get_resolution().values()
        if x_start < 0 or y_start < 0 or x_end > x_max or y_end > y_max:
            raise ValueError("Unsupported resolution")
        self.window = dict(x_start=x_start, y_start=y_start, x_end=x_end, y_end=y_end)

    def get_skipping(self):
        return self.skipping

    def set_skipping(self, x_skip, y_skip):
        self.skipping = dict(x_skip=x_skip, y_skip=y_skip)

    def get_binning(self):
        return self.binning

    def set_binning(self, x_binning, y_binning):
        self.binning = dict(x_binning=x_binning, y_binning=y_binning)

    def get_frame_rate(self):
        return self.frame_rate

    def set_frame_rate(self, fps):
        self.frame_rate = fps

    def get_exposure_time(self):
        return self.exposure_time

    def set_exposure_time(self, ms):
        self.exposure_time = ms

    def get_analog_gain(self):
        return self.analog_gain

    def set_analog_gain(self, multiply):
        self.analog_gain = multiply

    def get_digital_gain(self):
        return self.digital_gain

    def set_digital_gain(self, multiply):
        self.digital_gain = multiply

    def get_color_gains(self):
        return self.color_gains

    def set_color_gains(self, r, g1, g2, b):
        self.color_gains = dict(r=r, g1=g1, g2=g2, b=b)
