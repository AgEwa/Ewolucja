import numpy as np


class Grid:
    EMPTY = 0
    BARRIER = -1

    def __init__(self, size_x, size_y):
        self.width = size_x
        self.height = size_y

        self.data = np.zeros((size_x, size_y), dtype=np.int16)

        return

    def in_bounds(self, loc):
        return 0 <= loc[0] < self.width and 0 <= loc[1] < self.height

    def at(self, loc):
        return self.data[loc[0], loc[1]]

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
        return potentials[np.random.choice(potentials.shape[0])]
