from math import hypot
from typing import Callable

# py -m pip install attrs
# py -m pip install attrs
from attr import define, ib, validators
import matplotlib.pyplot as plt


@define
class Point:
    _x: ib(validator=validators.instance_of(float | int))
    _y: ib(validator=validators.instance_of(float | int))

    @classmethod
    def from_tuples(cls, tuples: list[tuple[int, int]]):
        return [Point.from_tuple(tup) for tup in tuples]

    @classmethod
    def from_tuple(cls, tup: tuple[int, int]):
        return cls(*tup)

    @staticmethod
    def dist(point1, point2):
        return hypot(point2.x - point1.x, point2.y - point1.y)

    @staticmethod
    def tabulate(f: Callable, domain: range):
        if not callable(f):
            raise ValueError('f(x) is not a function!')

        return [Point(x, f(x)) for x in domain]

    @staticmethod
    def plot(points):
        tuples = tuple(map(lambda p: (p.x, p.y), points))
        plt.plot(*zip(*tuples))

    def __iter__(self):
        yield self.x, self.y

    def __repr__(self):
        return f'Point(x={self.x}, y={self.y})'

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, float | int):
            raise ValueError('Value is not a number')
        self._x = value

    @x.deleter
    def x(self):
        del self._x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, float | int):
            raise ValueError('Value is not a number')
        self._y = value

    @y.deleter
    def y(self):
        del self._x
