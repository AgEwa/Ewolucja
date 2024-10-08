import numpy as np

from src.typess import Coord


class Grid:
    EMPTY = 0
    BARRIER = -1

    def __init__(self, size_x, size_y):
        self.width = size_x
        self.height = size_y

        self.data = np.zeros((size_x, size_y), dtype=np.int16)

        return

    def in_bounds(self, loc):
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height

    def at(self, loc):
        return self.data[loc.x, loc.y]

    def is_empty_at(self, loc):
        return self.at(loc) == Grid.EMPTY

    def is_barrier_at(self, loc):
        return self.at(loc) == Grid.BARRIER

    def is_occupied_at(self, loc):
        return self.at(loc) != Grid.EMPTY and self.at(loc) != Grid.BARRIER

    def find_empty(self):
        # all indexes where grid is zero
        potentials = np.argwhere(self.data == 0)

        # select one such index randomly
        result = potentials[np.random.choice(potentials.shape[0])]

        return Coord(result[0].item(), result[1].item())

    # methods with x,y params to not force creation of Coord objects:

    def in_bounds_xy(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def at_xy(self, x, y):
        return self.data[x, y]

    def is_empty_at_xy(self, x, y):
        return self.at_xy(x, y) == Grid.EMPTY

    def is_barrier_at_xy(self, x, y):
        return self.at_xy(x, y) == Grid.BARRIER

    def is_occupied_at_xy(self, x, y):
        return self.at_xy(x, y) != Grid.EMPTY and self.at_xy(x, y) != Grid.BARRIER
