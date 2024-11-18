import numpy as np

from src.LocationTypes import Coord


class Grid:
    EMPTY = [0, -2]  # Food does not occupy space
    BARRIER = -1
    FOOD = -2

    def __init__(self, size_x, size_y):
        self.width = size_x
        self.height = size_y

        self.data = np.zeros((size_x, size_y), dtype=np.int16)

        return

    def reset(self):
        self.data = np.zeros((self.width, self.height), dtype=np.int16)

        return

    def in_bounds(self, loc: Coord):
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height

    def at(self, loc: Coord):
        return self.data[loc.x, loc.y]

    def is_empty_at(self, loc: Coord):
        return self.at(loc) in Grid.EMPTY

    def is_barrier_at(self, loc: Coord):
        return self.at(loc) == Grid.BARRIER

    def is_occupied_at(self, loc: Coord):
        return self.at(loc) not in Grid.EMPTY and self.at(loc) != Grid.BARRIER

    def is_food_at(self, loc: Coord):
        return self.at(loc) == Grid.FOOD

    def find_empty(self) -> Coord:
        # all indexes where grid is zero
        potentials = np.argwhere(np.isin(self.data, Grid.EMPTY))

        # select one such index randomly
        result = potentials[np.random.choice(potentials.shape[0])]

        return Coord(result[0].item(), result[1].item())

    # methods with x,y params to not force creation of Coord objects:

    def in_bounds_xy(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def at_xy(self, x, y):
        return self.data[x, y]

    def is_empty_at_xy(self, x, y):
        return self.at_xy(x, y) in Grid.EMPTY

    def is_barrier_at_xy(self, x, y):
        return self.at_xy(x, y) == Grid.BARRIER

    def is_occupied_at_xy(self, x, y):
        return self.at_xy(x, y) not in Grid.EMPTY and self.at_xy(x, y) != Grid.BARRIER

    def is_food_at_xy(self, x, y):
        return self.at_xy(x, y) == Grid.FOOD
