import pytest
from prop_methods import property_getters_setters

@pytest.fixture
def prop():
    class Props:
        def __init__(self):
            self._foo = 1

        @property
        def foo(self):
            return self._foo

        @foo.setter
        def foo(self, value):
            self._foo = value
            return self._foo
    return Props

@pytest.fixture
def prop_gs(prop):
    return property_getters_setters(prop)

def test_get(prop_gs):
    assert prop_gs.foo() == "foo is 1"


def test_set(prop_gs):
    assert prop_gs.foo(2) == "set foo to 2"
    assert prop_gs.foo() == "foo is 2"
