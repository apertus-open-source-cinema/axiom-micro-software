from inspect import ismethod


def typed(*types):
    """
    Casts the arguments of the decorated function with the given casting functions

    :param types: the list of types the decorated function should recive
    :return: the casted function
    """

    def decorator(func):
        def to_return(*args):
            casted_args = []
            for (i, (cast, arg)) in enumerate(zip(types, args)):
                if ismethod(func) and i == 0:
                    arg = arg
                else:
                    if type(cast) == function:
                        arg = cast(arg)
                    elif type(cast) == dict:
                        arg = {key: cast(arg) for (arg, (key, value)) in zip(args, cast)}
                    else:
                        # assume iterable
                        arg = [cast(arg) for (cast, arg) in enumerate(zip(types, args))]
                casted_args.append(arg)
            return func(*casted_args)
        return to_return
    return decorator


def noop(a):
    return a


def test_type_decorator():
    @typed(int)
    def add(a, b):
        return a + b

    assert add("1", "2") == 3
