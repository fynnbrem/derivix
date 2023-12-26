from dataclasses import dataclass
from typing import TypeVar, Generic, Any, Callable


@dataclass
class MutableBool:
    state: bool


T = TypeVar("T")


class Subscribable(Generic[T]):
    subscribers: list[Callable[[T], Any]]
    _val: T

    def __init__(self, value: T):
        self._val: T = value
        self.subscribers = list()

    @property
    def val(self) -> T:
        return self._val

    @val.setter
    def val(self, value: T):
        self._val = value
        for subscriber in self.subscribers:
            subscriber(value)


class SharedAttribute(Generic[T]):
    """A class as extension to a regular attribute.
    This class holds a value like a regular attribute,
    but can then be passed to other objects so each object refers to the same attribute.

    The data is stored in `self.value` and can be accessed as a property over the abbreviation `self.v`
    or the getter/setter `self.get()`/`self.set()`.

    The constructor takes an initial `value`. If the `value` is `None`, this object's `self.value` will not be set.
    To apply the initial value even it is `None`, use `set_none`.


    This class is intended as streamlined solution to sharing attributes via explicit getters/setters within the Class.
    It also removes the need to have a hosting class that defines the getters/setters.
     This object will be hosted by whichever objects have a reference to it.
    """
    value: T

    def __init__(self, value: T = None, set_none=False):
        if value is not None or set_none:
            self.value = value


    @property
    def v(self) -> T:
        return self.value

    @v.setter
    def v(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

    def set(self, value: T):
        self.value = value

if __name__ == '__main__':
    x = SharedAttribute()
    x.v = 1
    print(x.v)