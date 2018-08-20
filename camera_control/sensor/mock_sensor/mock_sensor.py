from camera_control.propfs.type_decorators import typed
from camera_control.sensor.sensor import Sensor


class MockSensor(Sensor):
    @staticmethod
    def get_sensor():
        pass

    def __init__(self):
        self.window = (0, 0, *self.resolution)
        self.skipping = (0, 0)
        self.binning = (0, 0)
        self.frame_rate = 60
        self.exposure_time = 10
        self.analog_gain = 1.0
        self.digital_gain = 1.0
        self.color_gains = (1.0, 1.0, 1.0, 1.0)

    @property
    def resolution(self):
        return (1280, 720)

    @property
    def window(self):
        return self._window

    @window.setter
    @typed({"x_start": int, "y_start": int, "x_end": int, "y_end": int})
    def window(self, value):
        x_max, y_max = self.resolution
        if value["x_start"] < 0 or value["y_start"] < 0 or value["x_end"] > x_max or value["y_end"] > y_max:
            raise ValueError("Unsupported resolution")
        self._window = value

    @property
    def skipping(self):
        return self._skipping

    @skipping.setter
    @typed({"x_skip": int, "y_skip": int})
    def skipping(self, value):
        self._skipping = value

    @property
    def binning(self):
        return self._binning

    @binning.setter
    @typed({"x_binning": int, "y_binning": int})
    def binning(self, value):
        self._binning = value

    @property
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    @typed(float)
    def frame_rate(self, fps):
        self._frame_rate = fps

    @property
    def exposure_time(self):
        return self._exposure_time

    @exposure_time.setter
    @typed(float)
    def exposure_time(self, ms):
        self._exposure_time = ms

    @property
    def analog_gain(self):
        return self._analog_gain

    @analog_gain.setter
    @typed(float)
    def analog_gain(self, multiply):
        self._analog_gain = multiply

    @property
    def digital_gain(self):
        return self._digital_gain

    @digital_gain.setter
    @typed(float)
    def digital_gain(self, multiply):
        self._digital_gain = multiply

    @property
    def color_gains(self):
        return self._color_gains

    @color_gains.setter
    @typed({"red": float, "green1": float, "green2": float, "blue": float})
    def color_gains(self, value):
        self._color_gains = value
