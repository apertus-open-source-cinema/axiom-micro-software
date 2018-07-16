import os.path
from yaml import load
from sensor_control.util import RelativeOpener

class ProfileIncompatibleError(ValueError):
    pass

class ProfileManager:
    """Keeps track of and applies new profiles to a sensor"""
    def __init__(self, sensor, path=__file__):
        self.sensor = sensor
        self.path = os.path.abspath(path)
        self._open = RelativeOpener(self.path).open

        self._profile = None

    @property
    def available_profiles(self):
        files = os.listdir(self.path)
        f = lambda name: True if name.endswith(".yml") else False
        return filter(f, files)

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        if os.path.exists(profile) and profile.endswith("yml"):
            # profile is already a valid path, dont't look in default path
            p_file = open(profile)
        else:
            p_file = self._open(profile)

        p = load(p_file)
            
        try:
            for key, val in p:
                setattr(sensor, key, val)
        except AttributeError:
            # TODO: Try to roll back to previous profile/settings?
            raise ProfileIncompatibleError("Profile couldn't be applied (%)" % key)
            
        

