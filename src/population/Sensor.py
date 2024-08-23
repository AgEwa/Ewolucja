import random

import config
from src.external import grid
from src.population.Neuron import Neuron
from src.population.SensorActionEnums import NeuronType, SensorType
from src.types import Compass
from utils.Oscilator import Oscillator


class Sensor(Neuron):
    def __init__(self, sensor_type, specimen):
        super().__init__(NeuronType.SENSOR)
        self.sensor_type = sensor_type
        self.specimen = specimen
        self.oscillator = Oscillator(1 / specimen.oscPeriod)
        #self.value = 5

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
            SensorType.LAST_MOVE_DIST_X: self._get_last_move_dir_x,
            SensorType.LAST_MOVE_DIST_Y: self._get_last_move_dir_y,
            SensorType.POPULATION: self._get_population_density_in_neighbourhood(),
            SensorType.POPULATION_LR: self._get_population_density_left_right(),
            SensorType.POPULATION_FWD: self._get_population_density_forward_reverse(),
            }

        method = sensor_value_methods.get(self.sensor_type)
        if method:
            self.value = method()

    def _get_oscillator_value(self):
        return self.oscillator.get_value()

    def _get_specimen_age(self):
        return self.specimen.age

    @staticmethod
    def _get_random_value():
        return random.uniform(-1, 1)

    def _get_location_x(self):
        return self.specimen.location[1]

    def _get_location_y(self):
        return self.specimen.location[0]

    def _get_boundary_distance_x(self):
        return min(self.specimen.location[1], grid.width - self.specimen.location[1])

    def _get_boundary_distance_y(self):
        return min(self.specimen.location[0], grid.width - self.specimen.location[0])

    def _get_boundary_distance(self):
        x_dist = self._get_boundary_distance_x()
        y_dist = self._get_boundary_distance_y()
        return min(x_dist, y_dist)

    def _get_last_move_dir_y(self):
        match self.specimen.last_movement[0].dir:
            case Compass.NORTH | Compass.NORTH_EAST | Compass.NORTH_WEST:
                return self.specimen.last_movement[1]
            case Compass.SOUTH | Compass.SOUTH_EAST | Compass.SOUTH_WEST:
                return -self.specimen.last_movement[1]
            case _:
                return 0

    def _get_last_move_dir_x(self):
        match self.specimen.last_movement[0].dir:
            case Compass.EAST | Compass.NORTH_EAST | Compass.SOUTH_EAST:
                return self.specimen.last_movement[1]
            case Compass.WEST | Compass.NORTH_WEST | Compass.SOUTH_WEST:
                return -self.specimen.last_movement[1]
            case _:
                return 0

    def _get_population_density_in_neighbourhood(self):
        pop = 0
        for x in range(self.specimen.location[1] - config.NEIGHBOURHOOD_RADIUS,
                       self.specimen.location[1] + config.NEIGHBOURHOOD_RADIUS + 1):
            for y in range(self.specimen.location[0] - config.NEIGHBOURHOOD_RADIUS,
                           self.specimen.location[0] + config.NEIGHBOURHOOD_RADIUS + 1):
                if grid.is_occupied_at([y, x]):
                    pop += 1
        return pop / (4 * config.NEIGHBOURHOOD_RADIUS ** 2)

    def _get_population_density_left_right(self):
        if self.specimen.location[0].dir.value % 2 == 1:
            if self.specimen.location[0].dir in {Compass.NORTH, Compass.SOUTH}:
                self._get_simple_pop_dens_in_line("L-R")
            else:
                self._get_simple_pop_dens_in_line("U-D")
        else:
            if self.specimen.location[0].dir in {Compass.NORTH_WEST, Compass.SOUTH_EAST}:
                self._get_complex_pop_dens_in_line("L-U")
            else:
                self._get_complex_pop_dens_in_line("R-U")

    def _get_population_density_forward_reverse(self):
        if self.specimen.location[0].dir.value % 2 == 1:
            if self.specimen.location[0].dir in {Compass.NORTH, Compass.SOUTH}:
                self._get_simple_pop_dens_in_line("U-D")
            else:
                self._get_simple_pop_dens_in_line("L-R")
        else:
            if self.specimen.location[0].dir in {Compass.NORTH_WEST, Compass.SOUTH_EAST}:
                self._get_complex_pop_dens_in_line("R-U")
            else:
                self._get_complex_pop_dens_in_line("L-U")

    def _get_simple_pop_dens_in_line(self, direction):
        pop = 0
        if direction == "L-R":
            y = self.specimen.location[0]
            range_middle = self.specimen.location[1]
            for x in range(range_middle - config.NEIGHBOURHOOD_RADIUS, range_middle + config.NEIGHBOURHOOD_RADIUS + 1):
                if grid.is_occupied_at([y, x]):
                    pop += 1

        else:
            x = self.specimen.location[1]
            range_middle = self.specimen.location[0]
            for y in range(range_middle - config.NEIGHBOURHOOD_RADIUS, range_middle + config.NEIGHBOURHOOD_RADIUS + 1):
                if grid.is_occupied_at([y, x]):
                    pop += 1

        return pop / (2 * config.NEIGHBOURHOOD_RADIUS)

    def _get_complex_pop_dens_in_line(self, direction):
        pop = 0
        x = self.specimen.location[1]
        y = self.specimen.location[0]
        dir_change = 1 if direction == "R-U" else -1

        for i in range(-config.NEIGHBOURHOOD_RADIUS, config.NEIGHBOURHOOD_RADIUS + 1):
            if grid.is_occupied_at([(y - i)*dir_change, x - i]):
                pop += 1
            if grid.is_occupied_at([(y + i)*dir_change, x + i]):
                pop += 1
        return pop / (2 * config.NEIGHBOURHOOD_RADIUS)

    @staticmethod
    def __distance_between(loc_1, loc_2):
        return abs((loc_1[0] + loc_2[0]) ** 2 + (loc_1[1] + loc_2[1]) ** 2)
