import math
import random

import numpy as np
import scipy

import config
from src.saves.Settings import Settings
from src.world.LocationTypes import Coord, Conversions, Direction, Compass


class Grid:
    EMPTY = 0
    BARRIER = -1

    def __init__(self, size: int):
        self.size = size

        self.data = np.zeros((size, size), dtype=np.int16)
        self.food_data = {}
        self.barriers = []

        self.pheromones = self.Pheromones(size)
        return

    def reload_size(self):
        self.size = Settings.settings.dim
        self.data = np.zeros((self.size, self.size), dtype=np.int16)

    def reset(self):
        self.data = np.zeros((self.size, self.size), dtype=np.int16)
        for key in self.food_data:
            self.food_data[key] = random.randint(config.FOOD_PER_SOURCE_MIN, config.FOOD_PER_SOURCE_MAX)

        if self.barriers:
            xs, ys = zip(*self.barriers)
            self.data[xs, ys] = Grid.BARRIER

        return

    def clear(self):
        self.data = np.zeros((self.size, self.size), dtype=np.int16)
        self.food_data = {}
        self.barriers = []

        return

    def set_barriers_at_indexes(self, indexes: list[tuple]):
        xs, ys = zip(*indexes)
        assert self.in_bounds_xy(max(xs), max(ys)) and self.in_bounds_xy(min(xs), min(ys))
        assert (self.data[xs, ys] == Grid.EMPTY).all()
        self.data[xs, ys] = Grid.BARRIER
        self.barriers = indexes

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
        return 0 <= loc.x < self.size and 0 <= loc.y < self.size

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

    # def find_empty(self) -> Coord:
    #     # all indexes where grid is zero
    #     potentials = np.argwhere(self.data == Grid.EMPTY)
    #
    #     # select one such index randomly
    #     result = potentials[np.random.choice(potentials.shape[0])]
    #
    #     return Coord(result[0].item(), result[1].item())

    # methods with x,y params to not force creation of Coord objects:

    def food_eaten_at_xy(self, x, y):
        idx = (x, y)
        assert idx in self.food_data and self.food_data[idx] > 0
        self.food_data[idx] -= 1

    def in_bounds_xy(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

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

    class Pheromones:
        """
        Pheromone layer for the grid.
        """

        def __init__(self, size: int):
            self.size = size
            self.grid = np.zeros((size, size), dtype=np.float64)

        def emit(self, x: int, y: int, direction: Direction):
            strength = config.PHEROMONE_STRENGTH

            # This addresses the problem of specimen not moving?? (no pheromones emitted then)
            if direction.compass == Compass.CENTER:
                return

            else:
                backward_direction = direction.rotate_180_deg()
                backward_coord = Conversions.direction_as_normalized_coord(backward_direction)

                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        nx, ny = x + dx, y + dy
                        if 0 < nx < self.size - 1 and 0 < ny < self.size - 1:  # Pheromones not emitted at and out of the bounds
                            distance = math.sqrt(dx ** 2 + dy ** 2)
                            if distance > 3:
                                continue
                            # The dot product, due to orthogonality, disrupts emission in cells to the left and right,
                            # so we include some emission slightly to the side and in front of the specimen.
                            dx_norm, dy_norm = dx / (distance + 1e-6), dy / (distance + 1e-6)
                            backward_factor = max(0.01, np.dot([dx_norm, dy_norm], [backward_coord.x,
                                                                                    backward_coord.y]))
                            intensity = strength * backward_factor / (1 + distance)

                            # print(f"[DEBUG] Emitting at ({nx}, {ny}) with intensity {intensity}")
                            self.grid[nx, ny] += intensity

        def read(self, x: int, y: int, direction: Direction, axis: str) -> float:
            """
            Reads pheromone values in a specific axis: forward, left, or right.
            Args:
                x (int): The X-coordinate of the sensor.
                y (int): The Y-coordinate of the sensor.
                direction (Direction): The movement direction of the sensor.
                axis (str): The axis to read ("fwd" - forward, "r" - right, "l" - left).
            Returns:
                float: The average pheromone value in the specified axis.
            """
            pheromone_sum = 0
            count = 0

            base_coord = Conversions.direction_as_normalized_coord(direction)
            if axis == "fwd":
                modifier = base_coord
            elif axis == "r":
                modifier = Coord(-base_coord.y, base_coord.x)
            elif axis == "l":
                modifier = Coord(base_coord.y, -base_coord.x)
            else:
                raise ValueError("Invalid axis. Use 'fwd', 'r', or 'l'")

            # Read pheromones in the specified direction
            for i in range(1, 4):
                nx, ny = x + i * modifier.x, y + i * modifier.y
                if 0 < nx < self.size - 1 and 0 < ny < self.size - 1:
                    pheromone_sum += self.grid[nx, ny]
                    count += 1

            return pheromone_sum / max(1, count)

        def spread(self):
            """
            Pheromone spread and decay using convolution.
            """
            diffusion_rate = config.PHEROMONE_DIFFUSION_RATE
            decay_rate = config.PHEROMONE_DECAY_RATE

            self.grid *= (1 - decay_rate)

            diffusion_kernel = np.array([[0, diffusion_rate / 4, 0],
                                         [diffusion_rate / 4, 1 - diffusion_rate, diffusion_rate / 4],
                                         [0, diffusion_rate / 4, 0]])

            self.grid = scipy.ndimage.convolve(self.grid, diffusion_kernel, mode='constant', cval=0.0)

            self.grid[0, :] = 0
            self.grid[-1, :] = 0
            self.grid[:, 0] = 0
            self.grid[:, -1] = 0

