import random

from config import NEIGHBOURHOOD_RADIUS
from src.external import grid
from src.external import population
from src.population.SensorActionEnums import SensorType
from src.utils.utils import squeeze
from world.LocationTypes import Conversions, Direction


class Sensor:
    def __init__(self, types: set, specimen):
        self.types = types
        self.specimen = specimen

    def sense(self) -> dict:
        values = {}
        for type_id in self.types:
            method_name = f"_get_{SensorType(type_id).name.lower()}"
            method = getattr(self, method_name, None)
            if method:
                values[type_id] = squeeze(float(method()))
            else:
                values[type_id] = 0

        return values

    def _get_osc(self):
        """get oscillator value """
        return self.specimen.oscillator.get_value()

    def _get_age(self):
        """get specimen's age"""
        return self.specimen.age

    @staticmethod
    def _get_random():
        """get random value"""
        return random.uniform(-1, 1)

    def _get_loc_x(self):
        """get location x"""
        return self.specimen.location.x

    def _get_loc_y(self):
        """get location y"""
        return self.specimen.location.y

    def _get_boundary_dist_x(self):
        """get boundary distance x"""
        return min(self.specimen.location.x, grid.width - self.specimen.location.x)

    def _get_boundary_dist_y(self):
        """get boundary distance y"""
        return min(self.specimen.location.y, grid.height - self.specimen.location.y)

    def _get_boundary_dist(self):
        """get distance to the closest boundary"""
        x_dist = self._get_boundary_dist_x()
        y_dist = self._get_boundary_dist_y()
        return min(x_dist, y_dist)

    def _get_last_move_dist_y(self):
        return self.specimen.last_movement.y

    def _get_last_move_dist_x(self):
        return self.specimen.last_movement.x

    def _get_population(self):
        """get population density in neighbourhood"""
        number = 0
        for x in range(self.specimen.location.x - NEIGHBOURHOOD_RADIUS,
                       self.specimen.location.x + NEIGHBOURHOOD_RADIUS + 1):
            for y in range(self.specimen.location.y - NEIGHBOURHOOD_RADIUS,
                           self.specimen.location.y + NEIGHBOURHOOD_RADIUS + 1):

                if grid.in_bounds_xy(x, y) and grid.is_occupied_at_xy(x, y):
                    number += 1
        return number / (4 * NEIGHBOURHOOD_RADIUS ** 2)

    def _get_population_fwd(self):
        """get population density in forward-reverse axis"""
        return self._pop_density_in_line(self.specimen.last_movement_direction)

    def _get_population_lr(self):
        """get population density in left-right axis"""
        return self._pop_density_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _get_barrier_fwd(self):
        """get barrier dist in forward-reverse axis"""
        return self._dist_in_line("bar", self.specimen.last_movement_direction)

    def _get_barrier_lr(self):
        """get barrier dist in left-right axis"""
        return self._dist_in_line("bar", self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _dist_in_line(self, goal: str, direction: Direction):
        """get dist in line"""
        check = grid.is_barrier_at_xy if goal == "bar" else grid.is_food_at_xy
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        j = 1
        mod = Conversions.direction_as_normalized_coord(direction)  # returns -1/0/1 for x and y based on direction

        assert mod.x != 0 or mod.y != 0

        while (grid.in_bounds_xy(x + mod.x * i, y + mod.y * i)
               and not check(x + mod.x * i, y + mod.y * i)):
            i += 1

        while (grid.in_bounds_xy(x - mod.x * j, y - mod.y * j)
               and not check(x - mod.x * j, y - mod.y * j)):
            j += 1

        return min(i, j)

    def _pop_density_in_line(self, direction: Direction):
        """get density in line"""
        count = 0
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        j = 1

        mod = Conversions.direction_as_normalized_coord(direction)  # returns -1/0/1 for x and y based on direction

        assert mod.x != 0 or mod.y != 0

        while grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            if grid.is_occupied_at_xy(x + mod.x * i, y + mod.y * i):
                count += 1
            i += 1

        while grid.in_bounds_xy(x - mod.x * j, y - mod.y * j):
            if grid.is_occupied_at_xy(x - mod.x * j, y - mod.y * j):
                count += 1
            j += 1

        return count / (i + j - 1)

    def _get_longprobe_pop_fwd(self):
        """get distance to the closest member of population looking forward"""
        return self._look_forward("pop")

    def _get_longprobe_bar_fwd(self):
        """get distance to the closest barrier looking forward"""
        return self._look_forward("bar")

    def _get_genetic_sim_fwd(self):
        """get genetic similarity to the closest member of population looking forward"""
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        # modification for x and y
        mod = Conversions.direction_as_normalized_coord(self.specimen.last_movement_direction)
        # direction_as_normalized_coord returns -1/0/1 for x and y based on direction

        assert mod.x != 0 or mod.y != 0

        while (grid.in_bounds_xy(x + mod.x * i, y + mod.y * i)
               and not grid.is_occupied_at_xy(x + mod.x * i, y + mod.y * i)):
            i += 1

        if grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            idx = grid.at_xy(x + mod.x * i, y + mod.y * i)
            specimen = population[idx]
            return self._genetic_similarity(specimen.genome)
        return 0.0

    def _look_forward(self, goal: str):
        """
        find first looking forward within long_probe_dist.
        return distance.
        """
        check = grid.is_barrier_at_xy if goal == "bar" else grid.is_occupied_at_xy
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        # modification for x and y
        mod = Conversions.direction_as_normalized_coord(self.specimen.last_movement_direction)
        # direction_as_normalized_coord returns -1/0/1 for x and y based on direction

        assert mod.x != 0 or mod.y != 0

        while (grid.in_bounds_xy(x + mod.x * i, y + mod.y * i) and i < self.specimen.long_probe_dist
               and not check(x + mod.x * i, y + mod.y * i)):
            i += 1

        if goal == "pop_gen" and grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            idx = grid.at_xy(x + mod.x * i, y + mod.y * i)
            specimen = population[idx]
            return self._genetic_similarity(specimen.genome)

        return i

    def _genetic_similarity(self, genome2: list):
        """calculate genetic similarity for the specimen and passed genome"""
        genome1 = self.specimen.genome

        assert len(genome1) == len(genome2)

        total_similarity = 0
        max_similarity = len(genome1) * 32  # Each hex string (8 chars) represents 32 bits

        for gene1, gene2 in zip(genome1, genome2):
            # Convert hex strings to integers
            int1 = int(gene1, 16)
            int2 = int(gene2, 16)

            # XOR the two integers and count the number of differing bits
            differing_bits = bin(int1 ^ int2).count('1')

            # Calculate similarity for this pair
            similarity = 32 - differing_bits
            total_similarity += similarity

        # Calculate and return the percentage similarity
        return total_similarity / max_similarity

    def _get_food(self):
        """get food density in the neighbourhood"""
        number = 0
        for x in range(self.specimen.location.x - NEIGHBOURHOOD_RADIUS,
                       self.specimen.location.x + NEIGHBOURHOOD_RADIUS + 1):
            for y in range(self.specimen.location.y - NEIGHBOURHOOD_RADIUS,
                           self.specimen.location.y + NEIGHBOURHOOD_RADIUS + 1):

                if grid.in_bounds_xy(x, y) and grid.is_food_at_xy(x, y):
                    number += grid.food_data.get((x, y))
        return number / (4 * NEIGHBOURHOOD_RADIUS ** 2)

    def _get_food_fwd(self):
        """get food density in forward-reverse axis"""
        return self._food_density_in_line(self.specimen.last_movement_direction)

    def _get_food_lr(self):
        """get food density in left-right axis"""
        return self._food_density_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _food_density_in_line(self, direction: Direction):
        """get food density in line"""
        count = 0
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        j = 1

        mod = Conversions.direction_as_normalized_coord(direction)  # returns -1/0/1 for x and y based on direction

        assert mod.x != 0 or mod.y != 0

        while grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            if grid.is_food_at_xy(x + mod.x * i, y + mod.y * i):
                count += grid.food_data.get((x + mod.x * i, y + mod.y * i))
            i += 1

        while grid.in_bounds_xy(x - mod.x * j, y - mod.y * j):
            if grid.is_food_at_xy(x - mod.x * j, y - mod.y * j):
                count += grid.food_data.get((x - mod.x * j, y - mod.y * j))
            j += 1

        return count / (i + j - 1)

    def _get_food_dist_fwd(self):
        """get food dist in forward-reverse axis"""
        return self._dist_in_line("food", self.specimen.last_movement_direction)

    def _get_food_dist_lr(self):
        """get food dist in left-right axis"""
        return self._dist_in_line("food", self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _get_pheromone_fwd(self):
        return grid.pheromones.read(
            self.specimen.location.x,
            self.specimen.location.y,
            self.specimen.last_movement_direction,
            "fwd"
        )

    def _get_pheromone_l(self):
        return grid.pheromones.read(
            self.specimen.location.x,
            self.specimen.location.y,
            self.specimen.last_movement_direction,
            "l")

    def _get_pheromone_r(self):
        return grid.pheromones.read(
            self.specimen.location.x,
            self.specimen.location.y,
            self.specimen.last_movement_direction,
            "r")

    def _get_energy(self):
        return self.specimen.energy
