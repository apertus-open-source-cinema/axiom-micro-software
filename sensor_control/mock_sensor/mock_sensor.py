from sensor_control.sensor import Sensor
from sensor_control.util import to, to_tuple

class Mock_Sensor(Sensor):
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
    @to_tuple(int, 4)
    def window(self, value):
        xmax, ymax = self.resolution
        if value[0] < 0 or value[1] < 0 or value[2] > xmax or value[3] > ymax:
            raise ValueError("Unsupported resolution")
        self._window = value

    @property
    def skipping(self):
        return self._skipping

    @skipping.setter
    @to_tuple(int, 2)
    def skipping(self, value):
        self._skipping = value

    @property
    def binning(self):
        return self._binning

    @binning.setter
    @to_tuple(int, 2)
    def binning(self, value):
        self._binning = value

    @property
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    @to(int)
    def frame_rate(self, fps):
        self._frame_rate = fps

    @property
    def exposure_time(self):
        return self._exposure_time

    @exposure_time.setter
    @to(int)
    def exposure_time(self, ms):
        self._exposure_time = ms

    @property
    def analog_gain(self):
        return self._analog_gain
    
    @analog_gain.setter
    @to(float)
    def analog_gain(self, multiply):
        self._analog_gain = multiply

    @property
    def digital_gain(self):
        return self._digital_gain

    @digital_gain.setter
    @to(float)
    def digital_gain(self, multiply):
        self._digital_gain = multiply


    @property
    def color_gains(self):
        return self._color_gains

    @color_gains.setter
    @to_tuple(float, 4)
    def color_gains(self, value):
        self._color_gains = value
