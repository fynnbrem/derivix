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

