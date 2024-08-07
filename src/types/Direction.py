import numpy as np

from src.types.Compass import Compass


class Direction:
    def __init__(self, direction=Compass.CENTER):
        self.dir = direction

        return

    def rotate(self, n):
        # if original value was center, then rotation does nothing
        # else just offset clockwise
        return Direction(Compass.CENTER if self.dir == Compass.CENTER else Compass((self.dir.value + n) % 8))

    @staticmethod
    def random():
        return Direction(Compass.NORTH).rotate(np.random.choice(8))
