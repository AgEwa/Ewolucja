import math
from enum import Enum

import numpy as np


class Compass(Enum):
    NORTH_WEST = 0
    NORTH = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH = 5
    SOUTH_WEST = 6
    WEST = 7
    CENTER = 8


class Direction:
    __slots__ = ['compass']

    def __init__(self, p_compass: Compass = Compass.CENTER):
        assert isinstance(p_compass, Compass)

        self.compass = p_compass

        return

    def as_int(self) -> int:
        return self.compass.value

    def rotate(self, p_n: int = 0) -> 'Direction':
        assert isinstance(p_n, int)

        # if original value was center, then rotation does nothing
        # else just offset clockwise
        return Direction(Compass.CENTER if self.compass == Compass.CENTER else Compass((self.compass.value + p_n) % 8))

    # rotate 90 degrees clock-wise
    def rotate_90_deg_cw(self) -> 'Direction':
        return self.rotate(2)

    # rotate 90 degrees counter clock-wise
    def rotate_90_deg_ccw(self) -> 'Direction':
        return self.rotate(-2)

    # rotate 180 degrees
    def rotate_180_deg(self) -> 'Direction':
        return self.rotate(4)

    def __eq__(self, other: (Compass, 'Direction')):
        assert isinstance(other, (Compass, Direction))

        if isinstance(other, Compass):
            return self.as_int() == other.value

        return self.as_int() == other.as_int()

    def __ne__(self, other: (Compass, 'Direction')):
        assert isinstance(other, (Compass, Direction))

        if isinstance(other, Compass):
            return self.as_int() != other.value

        return self.as_int() != other.as_int()

    @staticmethod
    def random() -> 'Direction':
        return Direction(Compass.NORTH).rotate(np.random.choice(8))  # never center

    def __str__(self):
        return f'Direction({self.compass})'


class Coord:
    __slots__ = ['x', 'y']

    def __init__(self, p_x: int = 0, p_y: int = 0):
        assert isinstance(p_x, int) and isinstance(p_y, int)

        self.x = p_x
        self.y = p_y

        return

    def is_normalized(self) -> bool:
        return -1 <= self.x <= 1 and -1 <= self.y <= 1

    def normalize(self) -> 'Coord':
        return Conversions.direction_as_normalized_coord(Conversions.coord_as_direction(self))

    def length(self) -> int:
        return round(math.sqrt(self.x ** 2 + self.y ** 2))

    def __eq__(self, p_other: 'Coord'):
        assert isinstance(p_other, Coord)

        return self.x == p_other.x and self.y == p_other.y

    def __ne__(self, p_other: 'Coord'):
        assert isinstance(p_other, Coord)

        return self.x != p_other.x or self.y != p_other.y

    def __add__(self, p_other: ('Coord', Direction)):
        assert isinstance(p_other, (Coord, Direction))

        if isinstance(p_other, Coord):
            return Coord(self.x + p_other.x, self.y + p_other.y)

        return self + Conversions.direction_as_normalized_coord(p_other)

    def __sub__(self, p_other: ('Coord', Direction)):
        assert isinstance(p_other, (Coord, Direction))

        if isinstance(p_other, Coord):
            return Coord(self.x - p_other.x, self.y - p_other.y)

        return self - Conversions.direction_as_normalized_coord(p_other)

    def __mul__(self, p_other: int):
        assert isinstance(p_other, int)

        return Coord(self.x * p_other, self.y * p_other)

    def ray_sameness(self, p_other: ('Coord', Direction)):
        assert isinstance(p_other, (Coord, Direction))

        pass

    def __str__(self):
        return f'Coord({self.x}, {self.y})'

    def __repr__(self):
        return self.__str__()


class Conversions:
    @staticmethod
    def direction_as_normalized_coord(p_direction: Direction) -> 'Coord':
        assert isinstance(p_direction, Direction)

        match p_direction.compass:
            case Compass.NORTH_WEST:
                return Coord(-1, 1)
            case Compass.NORTH:
                return Coord(0, 1)
            case Compass.NORTH_EAST:
                return Coord(1, 1)
            case Compass.EAST:
                return Coord(1, 0)
            case Compass.SOUTH_EAST:
                return Coord(1, -1)
            case Compass.SOUTH:
                return Coord(0, -1)
            case Compass.SOUTH_WEST:
                return Coord(-1, -1)
            case Compass.WEST:
                return Coord(-1, 0)
            case Compass.CENTER:
                return Coord(0, 0)
            case _:
                raise Exception('ERROR: Unhandled enum Compass constant.')

    @staticmethod
    def coord_as_direction(p_coord: Coord) -> 'Direction':
        assert isinstance(p_coord, Coord)

        pos = np.array([[p_coord.x, p_coord.y]])
        alpha = np.pi / 8

        new_pos = pos @ np.array([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha), np.cos(alpha)]])
        new_x = new_pos[0, 0]
        new_y = new_pos[0, 1]

        if new_x > 0 and new_y >= 0:
            if new_y >= new_x:
                return Direction(Compass.NORTH)
            else:
                return Direction(Compass.NORTH_EAST)

        if new_x >= 0 and new_y < 0:
            if new_y >= -new_x:
                return Direction(Compass.EAST)
            else:
                return Direction(Compass.SOUTH_EAST)

        if new_x < 0 and new_y <= 0:
            if new_y <= new_x:
                return Direction(Compass.SOUTH)
            else:
                return Direction(Compass.SOUTH_WEST)

        if new_x <= 0 and new_y > 0:
            if new_y <= -new_x:
                return Direction(Compass.WEST)
            else:
                return Direction(Compass.NORTH_WEST)

        return Direction(Compass.CENTER)
