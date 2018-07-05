from abc import ABCMeta, abstractmethod


class Sensor(metaclass=ABCMeta):
    @staticmethod
    def get_sensor():
        """
        :returns: an initialized Sensor object for the current camera
        """

    @abstractmethod
    def __init__(self):
        """
        Here the image sensor should be initialized. After calling this method, the sensor should be up and running.
        """

    @abstractmethod
    def get_resolution(self):
        """
        :returns: A tuple of (max_x_resolution, max_y_resolution)
        """

    @abstractmethod
    def set_window(self, xmin, ymin, xmax, ymax):
        """
        Sets the readout window of the image sensor. If the window lays outside the possible range, a ValueError
        is thrown.
        :param xmin: the start y pixel. If this is 0 the readout window has no cropping to the left
        :param ymin: the start x pixel. If this is 0 the readout window has no cropping to the top
        :param xmax: the end x pixel.
        :param ymax: the end y pixel.
        """

    @abstractmethod
    def set_skipping(self, x, y):
        """
        Set the skipping value of the image sensor. If skiping is set to more than 0 in one direction, only every
        n-th pixel will be read out. If the skipping value is not supported by the sensor, a ValueError
        is thrown.
        :param x: the skipping in x direction
        :param y: the skipping in y direction
        """

    @abstractmethod
    def set_binning(self, x, y):
        """
        Set the binning value of the image sensor. If binning is set to more than 0 in one direction,
        n pixels will be averaged together. If the skipping value is not supported by the sensor, a ValueError
        is thrown.
        :param x: the skipping in x direction
        :param y: the skipping in y direction
        """

    @abstractmethod
    def set_frame_rate(self, fps):
        """
        Sets the number of frames per second, the sensor captures.
        If the desired value is unsupported, a ValueError is thrown.
        :param fps: the number of frames to capture per second.
        """

    @abstractmethod
    def set_exposure_time(self, ms):
        """
        Sets the exposure time for each frame. A higher value leads to a greater exposure time and therefore
        to more motion blur and a brighter image. The nearest value will be chosen, if the exact desired value is
        unsupported.
        :param ms: The desired number of milliseconds to expose each frame. This value may not be greater than 1/fps.
        :returns: The real set exposure time.
        """

    @abstractmethod
    def set_analog_gain(self, multiply):
        """
        Sets the analog gain of the sensor. The nearest value will be chosen, if the exact desired value is
        unsupported.
        :param multiply: a linear multiplication factor that incenses the base sensor sensitivity.
        :returns: The real set multiplication factor.
        """

    @abstractmethod
    def set_digital_gain(self, multiply):
        """
        Sets the digital gain of the sensor. The nearest value will be chosen, if the exact desired value is
        unsupported. Digital gain has only slight or none advantages compared to brightening the image in post.
        :param multiply: a linear multiplication factor that incenses the base sensor sensitivity.
        :returns: The real set multiplication factor.
        """

    @abstractmethod
    def set_color_gains(self, r, g1, g2, b):
        """
        Applies an individual, additional gain to each color. The nearest values will be chosen, if the exact desired
        values are unsupported. In most cases, this is implemented using digital gain.
        :param r: a linear multiplication factor for red
        :param g1: a linear multiplication factor for one half of the green sensels
        :param g2: a linear multiplication factor for the other half of the green sensels
        :param b: a linear multiplication factor for blue
        :returns: A tuple of the  real set multiplication factors.
        """
