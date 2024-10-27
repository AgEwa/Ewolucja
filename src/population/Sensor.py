import random

from config import NEIGHBOURHOOD_RADIUS
from src.external import grid
from src.external import pop as population
from src.population.Neuron import Neuron
from src.population.SensorActionEnums import NeuronType, SensorType
from src.typess import Conversions, Direction
from utils.Oscilator import Oscillator


class Sensor(Neuron):
    def __init__(self, sensor_type, specimen):
        super().__init__(NeuronType.SENSOR)
        self.sensor_type = sensor_type
        self.specimen = specimen
        self.oscillator = Oscillator(1 / specimen.osc_period)

    def sense(self):
        sensor_value_methods = {
            SensorType.OSC1: self._get_oscillator_value,
            SensorType.AGE: self._get_specimen_age,
            SensorType.RANDOM: self._get_random_value,
            SensorType.LOC_X: self._get_location_x,
            SensorType.LOC_Y: self._get_location_y,
            SensorType.BOUNDARY_DIST_X: self._get_boundary_distance_x,
            SensorType.BOUNDARY_DIST_Y: self._get_boundary_distance_y,
            SensorType.BOUNDARY_DIST: self._get_boundary_distance,
            SensorType.LAST_MOVE_DIST_X: self._get_last_move_dist_x,
            SensorType.LAST_MOVE_DIST_Y: self._get_last_move_dist_y,
            SensorType.POPULATION: self._get_population_density_in_neighbourhood,
            SensorType.POPULATION_LR: self._get_population_density_left_right,
            SensorType.POPULATION_FWD: self._get_population_density_forward_reverse,
            SensorType.BARRIER_FWD: self._get_barrier_dist_forward_reverse,
            SensorType.BARRIER_LR: self._get_barrier_dist_left_right,
            SensorType.LONGPROBE_POP_FWD: lambda: self._look_forward("pop"),
            SensorType.LONGPROBE_BAR_FWD: lambda: self._look_forward("bar"),
            SensorType.GENETIC_SIM_FWD: lambda: self._look_forward("pop_gen")
        }

        method = sensor_value_methods.get(self.sensor_type)
        if method:
            self.value = method()  # squeeze(float(method()))
        else:
            self.value = 0

    def _get_oscillator_value(self):
        return self.oscillator.get_value()

    def _get_specimen_age(self):
        return self.specimen.age

    @staticmethod
    def _get_random_value():
        return random.uniform(-1, 1)

    def _get_location_x(self):
        return self.specimen.location.x

    def _get_location_y(self):
        return self.specimen.location.y

    def _get_boundary_distance_x(self):
        return min(self.specimen.location.x, grid.width - self.specimen.location.x)

    def _get_boundary_distance_y(self):
        return min(self.specimen.location.y, grid.height - self.specimen.location.y)

    def _get_boundary_distance(self):
        x_dist = self._get_boundary_distance_x()
        y_dist = self._get_boundary_distance_y()
        return min(x_dist, y_dist)

    def _get_last_move_dist_y(self):
        return self.specimen.last_movement.y

    def _get_last_move_dist_x(self):
        return self.specimen.last_movement.x

    def _get_population_density_in_neighbourhood(self):
        pop = 0
        for x in range(self.specimen.location.x - NEIGHBOURHOOD_RADIUS,
                       self.specimen.location.x + NEIGHBOURHOOD_RADIUS + 1):
            for y in range(self.specimen.location.y - NEIGHBOURHOOD_RADIUS,
                           self.specimen.location.y + NEIGHBOURHOOD_RADIUS + 1):

                if grid.in_bounds_xy(x, y) and grid.is_occupied_at_xy(x, y):
                    pop += 1
        return pop / (4 * NEIGHBOURHOOD_RADIUS ** 2)

    def _get_population_density_forward_reverse(self):
        return self._pop_density_in_line(self.specimen.last_movement_direction)

    def _get_population_density_left_right(self):
        return self._pop_density_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _get_barrier_dist_forward_reverse(self):
        return self._barr_dist_in_line(self.specimen.last_movement_direction)

    def _get_barrier_dist_left_right(self):
        return self._barr_dist_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _barr_dist_in_line(self, direction: Direction):
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        j = 1
        mod = Conversions.direction_as_normalized_coord(direction)  # returns -1/0/1 for x and y based on direction

        while (grid.in_bounds_xy(x + mod.x * i, y + mod.y * i)
               and not grid.is_barrier_at_xy(x + mod.x * i, y + mod.y * i)):
            i += 1

        while (grid.in_bounds_xy(x - mod.x * j, y - mod.y * j)
               and not grid.is_barrier_at_xy(x - mod.x * j, y - mod.y * j)):
            j += 1

        return min(i, j)

    def _pop_density_in_line(self, direction: Direction):
        pop = 0
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        j = 1
        mod = Conversions.direction_as_normalized_coord(direction)  # returns -1/0/1 for x and y based on direction

        while grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            if grid.is_occupied_at_xy(x + mod.x * i, y + mod.y * i):
                pop += 1
            i += 1

        while grid.in_bounds_xy(x - mod.x * j, y - mod.y * j):
            if grid.is_occupied_at_xy(x - mod.x * j, y - mod.y * j):
                pop += 1
            j += 1

        return pop / (i + j - 1)

    def _look_forward(self, goal: str):
        check = grid.is_barrier_at_xy if goal == "bar" else grid.is_occupied_at_xy
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        # modification for x and y
        mod = Conversions.direction_as_normalized_coord(self.specimen.last_movement_direction)
        # direction_as_normalized_coord returns -1/0/1 for x and y based on direction

        while (grid.in_bounds_xy(x + mod.x * i, y + mod.y * i)
               and not check(x + mod.x * i, y + mod.y * i)):
            i += 1

        if goal == "pop_gen" and grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            idx = grid.at_xy(x + mod.x * i, y + mod.y * i)
            specimen = population[idx]
            return self._genetic_similarity(specimen.genome)

        return i

    def _genetic_similarity(self, genome2: str):
        genome1 = self.specimen.genome
        # Ensure both genomes have the same length
        if len(genome1) != len(genome2):
            raise ValueError("Genomes must be of the same length")

        total_similarity = 0
        max_similarity = len(genome1) * 32  # Each hex string (8 chars) represents 32 bits

        # Iterate through the genomes
        for gene1, gene2 in zip(genome1, genome2):
            # Convert hex strings to integers
            int1 = int(gene1, 16)
            int2 = int(gene2, 16)

            # XOR the two integers and count the number of differing bits
            differing_bits = bin(int1 ^ int2).count('1')

            # Calculate similarity for this pair (32 bits per 8-character hex string)
            similarity = 32 - differing_bits
            total_similarity += similarity

        # Calculate and return the percentage similarity
        return total_similarity / max_similarity

    # @staticmethod
    # def __distance_between(loc_1, loc_2):
    #     return abs((loc_1[0] + loc_2[0]) ** 2 + (loc_1[1] + loc_2[1]) ** 2)
