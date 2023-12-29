from enum import Enum, IntEnum
from typing import TypeVar, Generic, Callable, Optional, Tuple

T = TypeVar("T")


class Validity(IntEnum):
    """Enum for different levels of validity."""
    CLEAR = 0
    """The value is perfect."""
    INFO = 1
    """The value could be changed but works the same as the ideal value."""
    WARNING = 2
    """The value should be changed but the program will still run."""
    ERROR = 3
    """The value must be changed and the program will not run."""


class Validator(Generic[T]):
    """A simple class to assemble a complex validator.

    Allows a list of validators to be added on different levels, and when using `.validate()`,
    all these validators will be called on the passed value.

    The sub-validators will only be evaluated until the first one invalidates the value.
    Higher `Validity`-levels take precedence. Within one level, validators inserted earlier take precedence.
    """

    def __init__(self):
        self._sub_validators = {
            level: list() for level in
            sorted(set(Validity).difference({Validity.CLEAR}), reverse=True)
        }

    def add_validator(self, sub_validator: Callable[[T], Optional[str]], level: Validity):
        """Adds a sub-validator on the specified level.
        A sub-validator should be a Callable that takes the value as argument.
        The sub-validator must return a String specifying the issue if there is any, and `None` if there is no issue.

        The order of insertion matters: Within one level, validators inserted earlier take precedence.
        """
        if level == Validity.CLEAR:
            raise ValueError(
                f"Cannot add an validator for `{Validity.CLEAR.name}`.\n"
                f"This code will be returned automatically if there are no invalidities."
            )
        self.sub_validators[level].append(sub_validator)

    def validate(self, value: T) -> Optional[Tuple[Validity, str]]:
        """Validates the `value` using the defined sub-validators.
        The sub-validators will only be evaluated until the first one invalidates the value.
        Higher `Validity`-levels take precedence. Within one level, validators inserted earlier take precedence.
        """
        for level, sub_validators in self.sub_validators.items():
            # ↑ `self.validators` is already ordered so that the highest level will be evaluated first.
            for sub_validator in sub_validators:
                if text := sub_validator(value) is not None:
                    return text
        return None

    @property
    def sub_validators(self) -> dict[Validity, list[Callable[[T], Optional[str]]]]:
        """The sub-validators.
        To add a sub-validator, use `add_validator()`."""
        return self._sub_validators


if __name__ == '__main__':
    validator: Validator[str] = Validator()
