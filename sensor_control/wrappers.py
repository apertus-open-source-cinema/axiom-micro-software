from abc import ABCMeta 
import types
from sensor_control.profile_manager import ProfileManager

class Wrapper(metaclass=ABCMeta):
    """can wrap one or more classes to make their properties avaliable through methods.
    `_get_set_for_property() is used to generate these methods`
    
    Limitations: Two wrapped classes shouldn't have properties with the same name,
    the later one will shadow the earlier one."""
    def __init__(self, cls):
        self._sensor = cls()
        self._wrap_properties(self._sensor)
        self._profile_manager = ProfileManager(self._sensor)
        self._wrap_properties(self._profile_manager)

    def _wrap_properties(self, instance):
        """
        Generate and add methods to make `instance`'s properties accessible.
        This can be used to make properties of a class accessible through the fire library:
        `base_cmd prop` can be used to get the current value of `cls`'s property with the name `prop`.
        `base_cmd prop new_value` can be used to set the `prop` property to `new_value`
        :param instance: instance which properties this object shall expose as methods
        """
        # we need instance's class so we can easily get its properties
        cls = instance.__class__

        for name, prop in cls.__dict__.items():
            if name[0] is not "_" and isinstance(prop, property):
                setattr(self, name, types.MethodType(self._get_set_for_property(name, instance), self))

    @staticmethod
    def _get_set_for_property(name, instance):
        """
        Generate a get/set function for property with given name on the given instance.
        :param name: Name of the property the get/set-function should act on.
        :param instance: instance to act on
        :returns: Function that gets/sets property `name` in `instance`
        """



class CliWrapper(Wrapper):
    """Make properties available in a fire-cli-friendly way."""
    @staticmethod
    def _get_set_for_property(name, instance):
        """
        Generate a get/set function for property with given name.
        :param name: Name of the property the get/set-function should act on.
        :returns: Function that gets/sets property with name `name` in wrapped instance
        """
        def get_set(self, value=None):
            """
            Get or set and get property of wrapped instance
            :param value: New value for the property. If `None`, only get current value.
            """
            if value is None:
                return name + " is " + str(getattr(instance, name))
            else:
                setattr(instance, name, value)
                return "set " + name + " to " + str(value)
        return get_set

