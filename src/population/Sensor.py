import random

from config import NEIGHBOURHOOD_RADIUS
from src.LocationTypes import Conversions, Direction
from src.external import grid
from src.external import population
from src.population.Neuron import Neuron
from src.population.SensorActionEnums import NeuronType
from src.utils.Oscilator import Oscillator


class Sensor(Neuron):
    def __init__(self, sensor_type, specimen):
        super().__init__(NeuronType.SENSOR)
        self.sensor_type = sensor_type
        self.specimen = specimen
        self.oscillator = Oscillator(1 / specimen.osc_period)

    def sense(self):
        method_name = f"_get_{self.sensor_type.name.lower()}"
        method = getattr(self, method_name, None)
        if method:
            self.value = method()
        else:
            self.value = 0
        return

    def _get_osc(self):
        """ get oscillator value """
        return self.oscillator.get_value()

    def _get_age(self):
        """_get_specimen_age"""
        return self.specimen.age

    @staticmethod
    def _get_random():
        """_get_random_value"""
        return random.uniform(-1, 1)

    def _get_loc_x(self):
        """_get_location_x"""
        return self.specimen.location.x

    def _get_loc_y(self):
        """_get_location_y"""
        return self.specimen.location.y

    def _get_boundary_dist_x(self):
        """_get_boundary_distance_x"""
        return min(self.specimen.location.x, grid.width - self.specimen.location.x)

    def _get_boundary_dist_y(self):
        """_get_boundary_distance_y"""
        return min(self.specimen.location.y, grid.height - self.specimen.location.y)

    def _get_boundary_dist(self):
        """_get_boundary_distance"""
        x_dist = self._get_boundary_dist_x()
        y_dist = self._get_boundary_dist_y()
        return min(x_dist, y_dist)

    def _get_last_move_dist_y(self):
        return self.specimen.last_movement.y

    def _get_last_move_dist_x(self):
        return self.specimen.last_movement.x

    def _get_population(self):
        """_get_population_density_in_neighbourhood"""
        pop = 0
        for x in range(self.specimen.location.x - NEIGHBOURHOOD_RADIUS,
                       self.specimen.location.x + NEIGHBOURHOOD_RADIUS + 1):
            for y in range(self.specimen.location.y - NEIGHBOURHOOD_RADIUS,
                           self.specimen.location.y + NEIGHBOURHOOD_RADIUS + 1):

                if grid.in_bounds_xy(x, y) and grid.is_occupied_at_xy(x, y):
                    pop += 1

        return pop / (4 * NEIGHBOURHOOD_RADIUS ** 2)

    def _get_population_fwd(self):
        """_get_population_density_forward_reverse"""
        return self._pop_density_in_line(self.specimen.last_movement_direction)

    def _get_population_lr(self):
        """_get_population_density_left_right"""
        return self._pop_density_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _get_barrier_fwd(self):
        """_get_barrier_dist_forward_reverse"""
        return self._barr_dist_in_line(self.specimen.last_movement_direction)

    def _get_barrier_lr(self):
        """_get_barrier_dist_left_right"""
        return self._barr_dist_in_line(self.specimen.last_movement_direction.rotate_90_deg_cw())

    def _barr_dist_in_line(self, direction: Direction):
        """_barr_dist_in_line"""
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
        """_pop_density_in_line"""
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

    def _get_longprobe_pop_fwd(self):
        return self._look_forward("pop")

    def _get_longprobe_bar_fwd(self):
        return self._look_forward("bar")

    def _get_genetic_sim_fwd(self):
        return self._look_forward("pop_gen")

    def _look_forward(self, goal: str):
        check = grid.is_barrier_at_xy if goal == "bar" else grid.is_occupied_at_xy
        y = self.specimen.location.y
        x = self.specimen.location.x
        i = 1
        # modification for x and y
        mod = Conversions.direction_as_normalized_coord(self.specimen.last_movement_direction)
        # direction_as_normalized_coord returns -1/0/1 for x and y based on direction

        while grid.in_bounds_xy(x + mod.x * i, y + mod.y * i) and not check(x + mod.x * i, y + mod.y * i):
            i += 1

        if goal == "pop_gen" and grid.in_bounds_xy(x + mod.x * i, y + mod.y * i):
            idx = grid.at_xy(x + mod.x * i, y + mod.y * i)
            specimen = population[idx]
            return self._genetic_similarity(specimen.genome)

        return i

    def _genetic_similarity(self, genome2: list):
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
