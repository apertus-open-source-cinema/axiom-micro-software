import types

def property_getters_setters(cls):
    """
    Generate and add functions to cls to make its properties accessible through methods.
    This can be used to make properties of a class accessible through the fire library:
    `base_cmd prop` can be used to get the current value of `cls`'s property with the name `prop`.
    `base_cmd prop new_value` can be used to set the `prop` property to `new_value`
    :param cls: Class which properties shall be exposed as methods
    :returns: Class with a method with the same name as each property. See `get_set()`
    """
    class _wrap:
        def __init__(self, cls):
            self._instance = cls()

    def get_set_for_property(name):
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
                return name + " is " + str(getattr(self._instance, name))
            else:
                setattr(self._instance, name, value)
                return "set " + name + " to " + str(value)
        return get_set

    wrapper = _wrap(cls)

    for name, prop in cls.__dict__.items():
        if name[0] is not "_" and isinstance(prop, property):
            setattr(wrapper, name, types.MethodType(get_set_for_property(name), wrapper))

    return wrapper
