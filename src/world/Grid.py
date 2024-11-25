import random

import numpy as np

import config
from src.LocationTypes import Coord


class Grid:
    EMPTY = 0
    BARRIER = -1

    # FOOD_SOURCE = -2 'food trees' do not take whole space so specimens can stand in the same place as them so
    # theirs location and food left is remembered in a dict

    def __init__(self, size_x: int, size_y: int):
        self.width = size_x
        self.height = size_y

        self.data = np.zeros((size_x, size_y), dtype=np.int16)
        self.food_data = {}

        return

    def reset(self):
        self.data = np.zeros((self.width, self.height), dtype=np.int16)
        for key in self.food_data:
            self.food_data[key] = random.randint(config.FOOD_PER_SOURCE_MIN, config.FOOD_PER_SOURCE_MAX)

        return

    def set_barriers_at_indexes(self, indexes: list[tuple]):
        xs, ys = zip(*indexes)
        assert self.in_bounds_xy(max(xs), max(ys)) and self.in_bounds_xy(min(xs), min(ys))
        assert (self.data[xs, ys] == Grid.EMPTY).all()
        self.data[xs, ys] = Grid.BARRIER

    def set_food_sources_at_indexes(self, indexes: list[tuple]):
        xs, ys = zip(*indexes)
        assert self.in_bounds_xy(max(xs), max(ys)) and self.in_bounds_xy(min(xs), min(ys))
        assert (self.data[xs, ys] == Grid.EMPTY).all()
        # self.data[xs, ys] = Grid.FOOD_SOURCE
        self.food_data = {idx: random.randint(config.FOOD_PER_SOURCE_MIN, config.FOOD_PER_SOURCE_MAX) for idx in
                          indexes}

    def food_eaten_at(self, loc: Coord):
        idx = (loc.x, loc.y)
        assert idx in self.food_data
        self.food_data[idx] -= 1

    def in_bounds(self, loc: Coord):
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height

    def at(self, loc: Coord):
        return self.data[loc.x, loc.y]

    def is_empty_at(self, loc: Coord):
        return self.at(loc) == Grid.EMPTY

    def is_barrier_at(self, loc: Coord):
        return self.at(loc) == Grid.BARRIER

    def is_occupied_at(self, loc: Coord):
        return self.at(loc) != Grid.EMPTY and self.at(loc) != Grid.BARRIER

    def is_food_at(self, loc: Coord):
        return (loc.x, loc.y) in self.food_data and self.food_data.get((loc.x, loc.y)) > 0

    def find_empty(self) -> Coord:
        # all indexes where grid is zero
        potentials = np.argwhere(self.data == Grid.EMPTY)

        # select one such index randomly
        result = potentials[np.random.choice(potentials.shape[0])]

        return Coord(result[0].item(), result[1].item())

    # methods with x,y params to not force creation of Coord objects:

    def food_eaten_at_xy(self, x, y):
        idx = (x, y)
        assert idx in self.food_data and self.food_data[idx] > 0
        self.food_data[idx] -= 1

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

    def is_food_at_xy(self, x, y):
        return (x, y) in self.food_data and self.food_data.get((x, y)) > 0

