from typing import Callable, Optional, TypeVar

T = TypeVar('T')
Predicate = Callable[[T], bool]


def always_true(_: T) -> Predicate:
    return True


def always_false(_: T) -> Predicate:
    return False


def both(left: Optional[Predicate], right: Optional[Predicate]) -> Predicate:
    left = left or always_true
    right = right or always_true
    return lambda value: left(value) and right(value)


def either(left: Optional[Predicate], right: Optional[Predicate]) -> Predicate:
    left = left or always_false
    right = right or always_false
    return lambda value: left(value) or right(value)


def negate(match: Optional[Predicate]) -> Predicate:
    return always_false if match is None else lambda value: not match(value)
